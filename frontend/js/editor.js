/* ═══════════════════════════════════════════════════════════════════════
   CodeMirror Editor Integration
   ═══════════════════════════════════════════════════════════════════════ */

const editors = {};

const LANG_MODES = {
    python: 'python',
    java: 'text/x-java',
    cpp: 'text/x-c++src',
};

function initEditor(elementId, options = {}) {
    const el = document.getElementById(elementId);
    if (!el) return null;

    const defaults = {
        mode: 'python',
        theme: 'material-darker',
        lineNumbers: true,
        lineWrapping: true,
        indentUnit: 4,
        tabSize: 4,
        indentWithTabs: false,
        matchBrackets: true,
        autoCloseBrackets: true,
        readOnly: false,
        placeholder: '',
    };

    const config = { ...defaults, ...options };
    const editor = CodeMirror(el, config);

    editors[elementId] = editor;
    return editor;
}

function setEditorLanguage(editorId, language) {
    const editor = editors[editorId];
    if (editor) {
        editor.setOption('mode', LANG_MODES[language] || 'python');
    }
}

function getEditorValue(editorId) {
    const editor = editors[editorId];
    return editor ? editor.getValue() : '';
}

function setEditorValue(editorId, value) {
    const editor = editors[editorId];
    if (editor) {
        editor.setValue(value);
        setTimeout(() => editor.refresh(), 10);
    }
}

// Initialize all editors on page load
document.addEventListener('DOMContentLoaded', () => {
    // Generated code output (read-only)
    initEditor('generated-code-editor', {
        readOnly: true,
        lineNumbers: true,
        placeholder: '// Generated code will appear here...',
    });

    // Analyze code input
    initEditor('analyze-editor', {
        readOnly: false,
        placeholder: '# Paste your code here to analyze...',
    });

    // Compare editors
    initEditor('compare-editor1', {
        readOnly: false,
        placeholder: '# Paste first code snippet...',
    });

    initEditor('compare-editor2', {
        readOnly: false,
        placeholder: '# Paste second code snippet...',
    });

    // Upload preview (read-only)
    initEditor('upload-code-editor', {
        readOnly: true,
        lineNumbers: true,
    });

    // Set default content for analyze editor
    setEditorValue('analyze-editor', `def bubble_sort(arr):
    """Sort array using bubble sort algorithm."""
    n = len(arr)
    for i in range(n):
        for j in range(0, n - i - 1):
            if arr[j] > arr[j + 1]:
                arr[j], arr[j + 1] = arr[j + 1], arr[j]
    return arr

# Example usage
data = [64, 34, 25, 12, 22, 11, 90]
sorted_data = bubble_sort(data)
print("Sorted array:", sorted_data)`);
});
