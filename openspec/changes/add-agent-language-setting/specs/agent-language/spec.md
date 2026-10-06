# Agent language

## ADDED Requirements

### Requirement: Persistent agent output language
The application SHALL default to German agent output and allow the founder to select German or English. Unknown language codes SHALL be rejected. The setting SHALL survive restart.

#### Scenario: Existing installation
- WHEN persisted settings have no language field
- THEN agent language defaults to German.

#### Scenario: Language selected
- WHEN the founder saves English or German
- THEN subsequent live execution sections, including retrospectives, receive the selected language instruction for every provider.

### Requirement: Preserve output contracts
Language instructions SHALL translate natural-language output values and preserve schema keys, enum values, identifiers and exact source quotations. Existing artifacts SHALL remain unchanged.

#### Scenario: Structured output
- WHEN German is selected
- THEN model requests specify German prose while preserving JSON contract values.
