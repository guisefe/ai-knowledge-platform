# Text-to-SQL Spec

## Status

Deferred.

Text-to-SQL is not part of the evaluated RAG MVP. Keeping it in the first delivery would add a second security model, a second evaluation problem, and a separate execution boundary before the document-to-answer path has been proven.

The capability may return as an independent milestone after the RAG MVP meets its quality gates.

## Future entry criteria

Work on Text-to-SQL should begin only when:

- the RAG vertical slice is complete and measured;
- the target database and business use case are explicit;
- queries execute through a read-only role;
- allowed schemas and tables are defined;
- SQL validation and evaluation datasets have owners;
- latency and operational cost budgets are known.

This file intentionally contains no active endpoint contract.
