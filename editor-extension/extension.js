const { LanguageClient } = require('vscode-languageclient/node');
const vscode = require('vscode');

let client;

function activate(context) {
    const serverOptions = {
        command: 'python3',
        args: [context.asAbsolutePath('../src/lsp.py')]
    };

    const clientOptions = {
        documentSelector: [{ scheme: 'file', language: 'asylum' }],
        synchronize: {
            fileEvents: vscode.workspace.createFileSystemWatcher('**/*.asy')
        }
    };

    client = new LanguageClient(
        'asylumLSP',
        'Asylum Language Server',
        serverOptions,
        clientOptions
    );

    client.start();
}

function deactivate() {
    if (!client) {
        return undefined;
    }
    return client.stop();
}

module.exports = {
    activate,
    deactivate
};
