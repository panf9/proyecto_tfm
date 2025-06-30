import * as vscode from 'vscode';
import axios from 'axios';

export function activate(context: vscode.ExtensionContext) {
	const disposable = vscode.commands.registerCommand('code-commenter.addCodeComments', async () => {
		const editor = vscode.window.activeTextEditor;
		if (!editor) return;

		const code = editor.document.getText(editor.selection);
		if (!code) {
			vscode.window.showInformationMessage("No code selected.");
			return;
		}

		vscode.window.withProgress({
			location: vscode.ProgressLocation.Notification,
			title: "Generating comments...",
			cancellable: false
		}, async () => {
			try {
				const response = await axios.post('http://localhost:8000/comment', {
					code_clean: code
				});
				const commented = response.data.commented_code;

				editor.edit(editBuilder => {
					editBuilder.replace(editor.selection, commented);
				});
			} catch (error) {
				vscode.window.showErrorMessage("Error generating comments.");
			}
		});
	});

	context.subscriptions.push(disposable);
}


// This method is called when your extension is deactivated
export function deactivate() {}
