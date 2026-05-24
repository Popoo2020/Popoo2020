# Zones and Conduits Concept Model

This file provides a simple conceptual model for separating responsibilities, trust levels and communication paths between business IT and industrial technology environments.

## Example zones

| Zone | Purpose | Example assets | Governance focus |
|---|---|---|---|
| Business IT Zone | Standard business systems | Laptops, email, SaaS tools | Identity, endpoint security, user access |
| Engineering Zone | Engineering and maintenance work | Engineering workstations, configuration tools | Change control, privileged access, logging |
| Operations Zone | Operator-facing systems | HMI, operator consoles | Availability, role clarity, controlled access |
| Production Zone | Core process control | PLCs, controllers, production equipment | Stability, segmentation, limited change windows |

## Example conduits

| Conduit | Communication path | Control focus |
|---|---|---|
| Business IT to Engineering | Administrative access and documentation flows | MFA, approval, logging |
| Engineering to Operations | Configuration and support flows | Change process, named accountability |
| Operations to Production | Process visibility and control flows | Minimal access, monitored changes |

## Documentation principles

- Every zone should have an owner.
- Every conduit should have a business reason.
- Access paths should be documented and reviewed.
- Logging expectations should be explicit.
- Emergency access should be defined before it is needed.
