# Architecture

This document describes the architecture of the Metadata Registry Service, including its modular design, event-driven patterns, and integration points.

## Service Relationship Diagram

```
				+--------------------------+
				|  metadata-registry-svc   |
				|  (schemas, definitions)  |
				+-----------+--------------+
						^
						|
	  +---------------------------+---------------------------+
	  |                           |                           |
	  |                           |                           |
  +-----+-----+             +-------+-------+           +-------+-------+
  | component |             | expectation   |           | protocol      |
  | registry  |             | registry      |           | registry      |
  |   svc     |             |   svc         |           |   svc         |
  +-----+-----+             +-------+-------+           +-------+-------+
	  |                           |                           |
	  |                           |                           |
	  v                           v                           v
   (references schemas,      (references schemas,         (references schemas,
    contracts, types)         rules, types)                message formats)
```

**Legend:**
- All domain registries reference schemas/definitions in the metadata-registry-svc.
- metadata-registry-svc is the single source of truth for all metadata.
