import sys
import logging
from pygls.server import LanguageServer
from lsprotocol.types import (
    TEXT_DOCUMENT_DID_OPEN,
    TEXT_DOCUMENT_DID_CHANGE,
    TEXT_DOCUMENT_COMPLETION,
    CompletionItem,
    CompletionList,
    Diagnostic,
    Position,
    Range,
    DidOpenTextDocumentParams,
    DidChangeTextDocumentParams,
    CompletionParams
)
from lark import UnexpectedToken, UnexpectedCharacters
from parser import parse

logging.basicConfig(filename="lsp.log", level=logging.DEBUG)
server = LanguageServer("asylum-lsp", "v0.1")

KEYWORDS = ["import", "let", "byte", "int", "float", "func", "if", "else", "while", "for", "return", "print", "read"]

def validate(ls: LanguageServer, uri: str, text: str):
    diagnostics = []
    try:
        parse(text)
    except UnexpectedToken as e:
        line = e.line - 1
        col = e.column - 1
        d = Diagnostic(
            range=Range(
                start=Position(line=line, character=col),
                end=Position(line=line, character=col + 1)
            ),
            message=f"Syntax Error: Unexpected token {repr(e.token)}",
            source="Asylum"
        )
        diagnostics.append(d)
    except UnexpectedCharacters as e:
        line = e.line - 1
        col = e.column - 1
        d = Diagnostic(
            range=Range(
                start=Position(line=line, character=col),
                end=Position(line=line, character=col + 1)
            ),
            message=f"Syntax Error: Unexpected characters",
            source="Asylum"
        )
        diagnostics.append(d)
    except Exception as e:
        pass
        
    ls.publish_diagnostics(uri, diagnostics)

@server.feature(TEXT_DOCUMENT_DID_OPEN)
def did_open(ls, params: DidOpenTextDocumentParams):
    doc = ls.workspace.get_text_document(params.text_document.uri)
    validate(ls, params.text_document.uri, doc.source)

@server.feature(TEXT_DOCUMENT_DID_CHANGE)
def did_change(ls, params: DidChangeTextDocumentParams):
    doc = ls.workspace.get_text_document(params.text_document.uri)
    validate(ls, params.text_document.uri, doc.source)

@server.feature(TEXT_DOCUMENT_COMPLETION)
def completions(ls, params: CompletionParams):
    items = []
    for kw in KEYWORDS:
        items.append(CompletionItem(label=kw))
    return CompletionList(is_incomplete=False, items=items)

if __name__ == '__main__':
    server.start_io()
