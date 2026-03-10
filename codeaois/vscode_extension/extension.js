const vscode = require('vscode');
const { exec } = require('child_process');

class CodeAOISChatProvider {
    resolveWebviewView(webviewView, context, token) {
        // Allow scripts in the webview
        webviewView.webview.options = { enableScripts: true };
        
        // Inject our HTML UI
        webviewView.webview.html = getWebviewContent();

        // Handle messages from the UI
        webviewView.webview.onDidReceiveMessage(message => {
            if (message.command === 'sendTask') {
                webviewView.webview.postMessage({ command: 'receiveMessage', text: '🤖 *CodeAOIS team is working...*' });

                const codeAoisPath = '/home/nikhil/codeaois';
                const pythonPath = '/home/nikhil/codeaois/aois_env/bin/python';
                const commandToRun = `"${pythonPath}" -m cli.main "${message.text}"`;

                exec(commandToRun, { cwd: codeAoisPath }, (err, stdout, stderr) => {
                    let response = stdout;
                    if (err) response = `Error: ${err.message}`;
                    if (stderr && !stderr.includes("already exists")) {
                        response += `\nStderr: ${stderr}`;
                    }
                    webviewView.webview.postMessage({ command: 'receiveMessage', text: response });
                });
            }
        });
    }
}

function activate(context) {
    // Register the sidebar provider
    const provider = new CodeAOISChatProvider();
    context.subscriptions.push(
        vscode.window.registerWebviewViewProvider('codeaois.chatView', provider)
    );
}

// The exact same HTML/CSS/JS UI as before!
function getWebviewContent() {
    return `<!DOCTYPE html>
    <html lang="en">
    <head>
        <style>
            body { font-family: sans-serif; padding: 10px; display: flex; flex-direction: column; height: 95vh; }
            #chat-box { flex-grow: 1; overflow-y: auto; margin-bottom: 10px; border: 1px solid #444; padding: 10px; background: #1e1e1e; color: #d4d4d4; white-space: pre-wrap; font-size: 13px;}
            #input-box { display: flex; flex-direction: column; gap: 5px; }
            #task-input { padding: 8px; background: #3c3c3c; color: white; border: 1px solid #555; width: 100%; box-sizing: border-box;}
            button { padding: 8px; background: #007acc; color: white; border: none; cursor: pointer; width: 100%; }
            button:hover { background: #005999; }
        </style>
    </head>
    <body>
        <div id="chat-box"></div>
        <div id="input-box">
            <input type="text" id="task-input" placeholder="Ask CodeAOIS..." />
            <button onclick="sendTask()">Send</button>
        </div>
        <script>
            const vscode = acquireVsCodeApi();
            const chatBox = document.getElementById('chat-box');
            const taskInput = document.getElementById('task-input');

            window.addEventListener('message', event => {
                const message = event.data;
                if (message.command === 'receiveMessage') {
                    chatBox.innerHTML += '<div><b>CodeAOIS:</b><br>' + message.text + '</div><hr>';
                    chatBox.scrollTop = chatBox.scrollHeight;
                }
            });

            function sendTask() {
                const text = taskInput.value;
                if (!text) return;
                chatBox.innerHTML += '<div><b>You:</b> ' + text + '</div><br>';
                vscode.postMessage({ command: 'sendTask', text: text });
                taskInput.value = '';
            }

            taskInput.addEventListener('keypress', function (e) {
                if (e.key === 'Enter') sendTask();
            });
        </script>
    </body>
    </html>`;
}

function deactivate() {}
module.exports = { activate, deactivate };