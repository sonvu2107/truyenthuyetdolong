using System;
using System.Collections.Generic;
using System.Drawing;
using System.IO;
using System.Runtime.InteropServices;
using System.Windows.Forms;
using System.Xml;

namespace AHTLLauncherFixed
{
    [ComVisible(true)]
    public sealed class LauncherBridge
    {
        private readonly LauncherForm owner;

        public LauncherBridge(LauncherForm owner)
        {
            this.owner = owner;
        }

        public bool ToggleFullscreen()
        {
            return owner.ToggleFullscreenSafe();
        }

        // GameFrame gọi callback này khi đã vào game, đổi URL nạp hoặc cập nhật
        // tên game. Nếu thiếu bridge, ExternalInterface có thể làm khung Flash đen.
        public bool JsCallClient(string code, string data, string reservedValue)
        {
            int callCode;
            if (!int.TryParse(code, out callCode))
                return true;
            return owner.HandleFlashClientCall(callCode, data);
        }
    }

    public sealed class LauncherForm : Form
    {
        private readonly WebBrowser browser;
        private bool isFullscreen;
        private Rectangle restoreBounds;
        private FormBorderStyle restoreBorderStyle;
        private FormWindowState restoreWindowState;

        public LauncherForm()
        {
            Text = "Ám Hắc Đồ Long OL";
            Icon = LoadLauncherIcon();
            StartPosition = FormStartPosition.CenterScreen;
            AutoScaleMode = AutoScaleMode.None;
            MinimumSize = new Size(800, 600);
            KeyPreview = true;

            IDictionary<string, string> config = ReadIni(Path.Combine(AppDomain.CurrentDomain.BaseDirectory, "config.ini"));
            ClientSize = new Size(ReadInt(config, "window_w", 1024), ReadInt(config, "window_h", 680));

            browser = new WebBrowser();
            browser.Dock = DockStyle.Fill;
            browser.ScriptErrorsSuppressed = true;
            browser.IsWebBrowserContextMenuEnabled = false;
            browser.AllowWebBrowserDrop = false;
            browser.ObjectForScripting = new LauncherBridge(this);
            browser.PreviewKeyDown += BrowserPreviewKeyDown;
            Controls.Add(browser);

            KeyDown += LauncherKeyDown;
            Shown += delegate { browser.Navigate(AddCacheBuster(ReadLoginUrl())); };
        }

        private static Icon LoadLauncherIcon()
        {
            string path = Path.Combine(AppDomain.CurrentDomain.BaseDirectory, "48x48.ico");
            try { return File.Exists(path) ? new Icon(path) : SystemIcons.Application; }
            catch { return SystemIcons.Application; }
        }

        private string ReadLoginUrl()
        {
            string path = Path.Combine(AppDomain.CurrentDomain.BaseDirectory, "config.xml");
            try
            {
                XmlDocument document = new XmlDocument();
                document.Load(path);
                XmlNode node = document.SelectSingleNode("/items/item[@name='loginURL']");
                if (node != null && node.Attributes != null && node.Attributes["url"] != null)
                    return node.Attributes["url"].Value;
            }
            catch (Exception error)
            {
                MessageBox.Show("Không đọc được config.xml: " + error.Message, Text,
                    MessageBoxButtons.OK, MessageBoxIcon.Error);
            }
            return "http://180.93.244.31:81/client_login.php";
        }

        private static string AddCacheBuster(string url)
        {
            string separator = url.Contains("?") ? "&" : "?";
            return url + separator + "_cb=" + DateTime.UtcNow.Ticks;
        }

        private static IDictionary<string, string> ReadIni(string path)
        {
            Dictionary<string, string> values = new Dictionary<string, string>(StringComparer.OrdinalIgnoreCase);
            if (!File.Exists(path)) return values;
            foreach (string rawLine in File.ReadAllLines(path))
            {
                string line = rawLine.Trim();
                if (line.Length == 0 || line.StartsWith(";") || line.StartsWith("[") || !line.Contains("="))
                    continue;
                int separator = line.IndexOf('=');
                values[line.Substring(0, separator).Trim()] = line.Substring(separator + 1).Trim();
            }
            return values;
        }

        private static int ReadInt(IDictionary<string, string> values, string key, int fallback)
        {
            string raw;
            int result;
            return values.TryGetValue(key, out raw) && int.TryParse(raw, out result) ? result : fallback;
        }

        public bool ToggleFullscreenSafe()
        {
            if (InvokeRequired)
                return (bool)Invoke(new Func<bool>(ToggleFullscreenSafe));

            SuspendLayout();
            if (!isFullscreen)
            {
                restoreBounds = Bounds;
                restoreBorderStyle = FormBorderStyle;
                restoreWindowState = WindowState;
                WindowState = FormWindowState.Normal;
                FormBorderStyle = FormBorderStyle.None;
                WindowState = FormWindowState.Maximized;
                isFullscreen = true;
            }
            else
            {
                WindowState = FormWindowState.Normal;
                FormBorderStyle = restoreBorderStyle;
                Bounds = restoreBounds;
                WindowState = restoreWindowState == FormWindowState.Minimized
                    ? FormWindowState.Normal
                    : restoreWindowState;
                isFullscreen = false;
            }
            ResumeLayout(true);
            return isFullscreen;
        }

        public bool HandleFlashClientCall(int callCode, string data)
        {
            if (InvokeRequired)
                return (bool)Invoke(new Func<int, string, bool>(HandleFlashClientCall), callCode, data);

            switch (callCode)
            {
                case 1: // JF_EXIT
                    BeginInvoke(new MethodInvoker(Close));
                    break;
                case 2: // JF_REFLASH
                    browser.Refresh(WebBrowserRefreshOption.Completely);
                    break;
                case 6: // JF_GAME_INFO
                    if (!string.IsNullOrEmpty(data))
                        Text = data;
                    break;
            }
            return true;
        }

        private void LauncherKeyDown(object sender, KeyEventArgs eventArgs)
        {
            if (eventArgs.KeyCode == Keys.F11 || (eventArgs.KeyCode == Keys.Escape && isFullscreen))
            {
                ToggleFullscreenSafe();
                eventArgs.Handled = true;
                eventArgs.SuppressKeyPress = true;
            }
        }

        private void BrowserPreviewKeyDown(object sender, PreviewKeyDownEventArgs eventArgs)
        {
            if (eventArgs.KeyCode == Keys.F11 || (eventArgs.KeyCode == Keys.Escape && isFullscreen))
                ToggleFullscreenSafe();
        }

        [STAThread]
        private static void Main()
        {
            Application.EnableVisualStyles();
            Application.SetCompatibleTextRenderingDefault(false);
            Application.Run(new LauncherForm());
        }
    }
}
