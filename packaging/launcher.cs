using System;
using System.Diagnostics;
using System.IO;
using System.Windows.Forms;

internal static class Launcher
{
    [STAThread]
    private static int Main()
    {
        const string title = "Nicholas's Nice Necker Cube Experiment";
        try
        {
            string root = Path.GetDirectoryName(Application.ExecutablePath);
            string python = Path.Combine(root, "runtime", "pythonw.exe");
            string script = Path.Combine(root, "app", "bootstrap.py");
            if (!File.Exists(python) || !File.Exists(script))
                throw new FileNotFoundException("Application files are missing. Run the installer again.");
            var start = new ProcessStartInfo(python, "-E -s -B \"" + script + "\"");
            start.WorkingDirectory = Path.Combine(root, "app");
            start.UseShellExecute = false;
            start.CreateNoWindow = true;
            start.EnvironmentVariables.Remove("PYTHONHOME");
            start.EnvironmentVariables.Remove("PYTHONPATH");
            start.EnvironmentVariables["PYTHONNOUSERSITE"] = "1";
            start.EnvironmentVariables["PYTHONDONTWRITEBYTECODE"] = "1";
            using (var process = Process.Start(start))
            {
                process.WaitForExit();
                return process.ExitCode;
            }
        }
        catch (Exception error)
        {
            MessageBox.Show(error.Message, title, MessageBoxButtons.OK, MessageBoxIcon.Error);
            return 1;
        }
    }
}
