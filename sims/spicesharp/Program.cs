// Batch runner for SpiceSharpParser: parses one netlist, runs every simulation in it and
// writes the .SAVE exports, the .PRINT tables and the .MEAS results to stdout; with
// -r, every unknown of every simulation to a SPICE rawfile (ASCII), one plot each.
//
//   spicesharp [-r rawfile] netlist
//
// A netlist with LTspice A-devices or an LTspice ideal diode model is read in the LTspice
// dialect with the custom components, as upstream does for those netlists.
// Exit codes: 0 ok, 1 usage, 2 parse or translation errors, 3 simulation error.

using System;
using System.Collections.Generic;
using System.Diagnostics;
using System.Globalization;
using System.IO;
using System.Linq;
using System.Numerics;
using System.Text;
using System.Text.RegularExpressions;
using SpiceSharp.Simulations;
using SpiceSharpParser;
using SpiceSharpParser.Common;
using SpiceSharpParser.CustomComponents;

internal static class Program
{
    private static readonly CultureInfo Inv = CultureInfo.InvariantCulture;

    private static string Num(double v) => v.ToString("R", Inv);

    // the statements of a netlist (continuations joined) that need the LTspice dialect
    private static bool NeedsLtspice(string path)
    {
        var statements = new List<string>();
        foreach (var raw in File.ReadLines(path).Skip(1))
        {
            var line = raw.Trim();
            if (line.StartsWith("+") && statements.Count > 0)
            {
                statements[statements.Count - 1] += " " + line.Substring(1);
            }
            else if (line.Length > 0 && line[0] != '*')
            {
                statements.Add(line);
            }
        }

        return statements.Any(s => char.ToUpperInvariant(s[0]) == 'A'
            || Regex.IsMatch(s, @"^\.model\s+\S+\s+d\b.*\b(ron|roff|vfwd|vrev)\s*=", RegexOptions.IgnoreCase));
    }

    private static int Main(string[] args)
    {
        string rawPath = null;
        var files = new List<string>();
        for (int i = 0; i < args.Length; i++)
        {
            if (args[i] == "-r" && i + 1 < args.Length)
            {
                rawPath = args[++i];
            }
            else
            {
                files.Add(args[i]);
            }
        }

        if (files.Count != 1 || files[0].StartsWith("-"))
        {
            Console.Error.WriteLine("usage: spicesharp [-r rawfile] netlist");
            return 1;
        }

        string path = Path.GetFullPath(files[0]);
        var options = new SpiceCompileOptions { WorkingDirectory = Path.GetDirectoryName(path) };
        if (NeedsLtspice(path))
        {
            Console.WriteLine("* dialect LTspice with custom components");
            options.Dialect = SpiceDialect.LTspice;
            options.ConfigureReader = settings => settings.UseCustomComponents();
        }

        SpiceCompilationResult result;
        try
        {
            result = SpiceCompiler.CompileFile(path, options);
        }
        catch (Exception e)
        {
            Console.Error.WriteLine("error: parse: " + e);
            return 2;
        }

        foreach (var diagnostic in result.Diagnostics)
        {
            Console.Error.WriteLine(diagnostic);
        }

        if (!result.Success || result.Model == null)
        {
            Console.Error.WriteLine("error: netlist has errors, nothing simulated");
            return 2;
        }

        var model = result.Model;
        var raw = new StringBuilder();
        Console.WriteLine("* title " + model.Title);
        foreach (var simulation in model.Simulations)
        {
            var exports = model.Exports.Where(e => ReferenceEquals(e.Simulation, simulation)).ToList();
            var plot = new Plot(simulation);
            Console.WriteLine("* simulation " + simulation.Name);
            if (exports.Count > 0)
            {
                Console.WriteLine(string.Join(" ", new[] { Independent(simulation).Item1 }.Concat(exports.Select(e => e.Name))));
            }

            simulation.EventExportData += (sender, e) =>
            {
                if (exports.Count == 0)
                {
                    return;
                }

                var row = new List<string> { Independent(simulation).Item2 };
                foreach (var export in exports)
                {
                    double v;
                    try
                    {
                        v = export.Extract();
                    }
                    catch (Exception)
                    {
                        v = double.NaN;
                    }

                    row.Add(Num(v));
                }

                Console.WriteLine(string.Join(" ", row));
            };

            var watch = Stopwatch.StartNew();
            try
            {
                foreach (int code in simulation.InvokeEvents(simulation.Run(model.Circuit, -1)))
                {
                    if (rawPath != null && plot.Main(code))
                    {
                        plot.Add();
                    }
                }
            }
            catch (Exception e)
            {
                Console.Error.WriteLine("error: simulation " + simulation.Name + ": " + e);
                return 3;
            }

            Console.WriteLine("* analysis time " + Num(watch.Elapsed.TotalSeconds) + " s");
            plot.Write(raw);
        }

        foreach (var print in model.Prints)
        {
            Console.WriteLine("* print " + print.Name);
            Console.WriteLine(string.Join(" ", print.ColumnNames));
            foreach (var row in print.Rows)
            {
                Console.WriteLine(string.Join(" ", row.Columns.Select(Num)));
            }
        }

        foreach (var entry in model.Measurements.OrderBy(m => m.Key, StringComparer.Ordinal))
        {
            foreach (var m in entry.Value)
            {
                Console.WriteLine("* meas " + m.Name + " " + (m.Success ? Num(m.Value) : "failed") + " " + m.SimulationName);
            }
        }

        if (rawPath != null)
        {
            File.WriteAllText(rawPath, raw.ToString());
        }

        return 0;
    }

    // name and current value of the independent variable of a simulation
    private static Tuple<string, string> Independent(object simulation)
    {
        switch (simulation)
        {
            case Transient t:
                return Tuple.Create("time", SafeNum(() => t.Time));
            case AC ac:
                return Tuple.Create("frequency", SafeNum(() => ac.Frequency));
            case DC dc:
                return Tuple.Create("sweep", SafeNum(() => dc.GetCurrentSweepValue()[0]));
            default:
                return Tuple.Create("sweep", "0");
        }
    }

    private static string SafeNum(Func<double> f)
    {
        try
        {
            return Num(f());
        }
        catch (Exception)
        {
            return "nan";
        }
    }

    // every unknown of a simulation at every exported point
    private sealed class Plot
    {
        private readonly ISimulation simulation;
        private readonly List<string> names = new List<string>();
        private readonly List<int> indices = new List<int>();
        private readonly List<Complex[]> rows = new List<Complex[]>();
        private readonly bool complex;

        public Plot(ISimulation simulation)
        {
            this.simulation = simulation;
            complex = simulation is AC;
        }

        // the export of the analysis itself, not the operating point before it
        public bool Main(int code)
        {
            switch (simulation)
            {
                case Transient _:
                    return code == Transient.ExportTransient;
                case AC _:
                    return code == AC.ExportSmallSignal;
                case DC _:
                    return code == DC.ExportSweep;
                default:
                    return (code & Simulation.Exports) != 0;  // not setup or teardown
            }
        }

        private static string Name(IVariable variable)
        {
            string name = variable.Name.ToLowerInvariant();
            if (name.EndsWith("/branch") || name.EndsWith(".branch"))   // the separator of the parser
            {
                return "i(" + name.Substring(0, name.Length - "/branch".Length) + ")";
            }

            return "v(" + name + ")";
        }

        public void Add()
        {
            if (names.Count == 0)
            {
                var map = complex
                    ? simulation.GetState<IComplexSimulationState>().Map
                    : simulation.GetState<IBiasingSimulationState>().Map;
                foreach (var pair in map.Where(p => p.Value > 0).OrderBy(p => p.Value))
                {
                    names.Add(Name(pair.Key));
                    indices.Add(pair.Value);
                }
            }

            var row = new Complex[indices.Count + 1];
            row[0] = double.Parse(Independent(simulation).Item2 == "nan" ? "NaN" : Independent(simulation).Item2, Inv);
            if (complex)
            {
                var solution = simulation.GetState<IComplexSimulationState>().Solution;
                for (int k = 0; k < indices.Count; k++)
                {
                    row[k + 1] = solution[indices[k]];
                }
            }
            else
            {
                var solution = simulation.GetState<IBiasingSimulationState>().Solution;
                for (int k = 0; k < indices.Count; k++)
                {
                    row[k + 1] = solution[indices[k]];
                }
            }

            rows.Add(row);
        }

        public void Write(StringBuilder raw)
        {
            if (rows.Count == 0)
            {
                return;
            }

            string axis = Independent(simulation).Item1;
            raw.Append("Title: spicesharp\nDate: -\nPlotname: ").Append(simulation.Name).Append('\n');
            raw.Append("Flags: ").Append(complex ? "complex" : "real").Append('\n');
            raw.Append("No. Variables: ").Append(names.Count + 1).Append('\n');
            raw.Append("No. Points: ").Append(rows.Count).Append('\n');
            raw.Append("Variables:\n\t0\t").Append(axis).Append("\tnotype\n");
            for (int k = 0; k < names.Count; k++)
            {
                raw.Append('\t').Append(k + 1).Append('\t').Append(names[k]).Append("\tnotype\n");
            }

            raw.Append("Values:\n");
            for (int p = 0; p < rows.Count; p++)
            {
                raw.Append(p);
                foreach (var v in rows[p])
                {
                    raw.Append('\t').Append(complex ? Num(v.Real) + "," + Num(v.Imaginary) : Num(v.Real)).Append('\n');
                }
            }
        }
    }
}
