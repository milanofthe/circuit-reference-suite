// Batch runner for SpiceSharpParser: parses one netlist, runs every simulation in it and
// writes the .SAVE exports, the .PRINT tables and the .MEAS results to stdout.
//
//   spicesharp [--ltspice] netlist
//
// --ltspice reads the netlist in the LTspice dialect with the custom components
// (A-devices, ideal diodes, nonlinear passives), as upstream does for those decks.
// Exit codes: 0 ok, 1 usage, 2 parse or translation errors, 3 simulation error.

using System;
using System.Collections.Generic;
using System.Globalization;
using System.IO;
using System.Linq;
using SpiceSharp.Simulations;
using SpiceSharpParser;
using SpiceSharpParser.Common;
using SpiceSharpParser.CustomComponents;

internal static class Program
{
    private static readonly CultureInfo Inv = CultureInfo.InvariantCulture;

    private static string Num(double v) => v.ToString("R", Inv);

    private static int Main(string[] args)
    {
        bool ltspice = args.Contains("--ltspice");
        string[] files = args.Where(a => a != "--ltspice").ToArray();
        if (files.Length != 1 || files[0].StartsWith("-"))
        {
            Console.Error.WriteLine("usage: spicesharp [--ltspice] netlist");
            return 1;
        }

        string path = Path.GetFullPath(files[0]);
        var options = new SpiceCompileOptions { WorkingDirectory = Path.GetDirectoryName(path) };
        if (ltspice)
        {
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
        Console.WriteLine("* title " + model.Title);
        foreach (var simulation in model.Simulations)
        {
            var exports = model.Exports.Where(e => ReferenceEquals(e.Simulation, simulation)).ToList();
            Console.WriteLine("* simulation " + simulation.Name);
            if (exports.Count > 0)
            {
                Console.WriteLine(string.Join(" ", new[] { Independent(simulation).Item1 }.Concat(exports.Select(e => e.Name))));
                simulation.EventExportData += (sender, e) =>
                {
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
            }

            try
            {
                foreach (var _ in simulation.InvokeEvents(simulation.Run(model.Circuit, -1)))
                {
                }
            }
            catch (Exception e)
            {
                Console.Error.WriteLine("error: simulation " + simulation.Name + ": " + e);
                return 3;
            }
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
                return Tuple.Create("sweep", SafeJoin(() => dc.GetCurrentSweepValue()));
            default:
                return Tuple.Create("point", "0");
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

    private static string SafeJoin(Func<double[]> f)
    {
        try
        {
            return string.Join(",", f().Select(Num));
        }
        catch (Exception)
        {
            return "nan";
        }
    }
}
