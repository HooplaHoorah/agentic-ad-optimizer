# System Architecture

This document describes the high-level architecture of the Agentic Ad Optimizer and how the different modules interact. The system is designed as a set of loosely coupled services that can evolve independently and scale as needed.

## Modules

- **Data Ingestion & Analytics**: Collects campaign data such as impressions, clicks, conversions and audience attributes from advertising APIs and internal sources. Stores this data in a secure, scalable database and exposes analytics through an API.

- **Creative Generator**: Uses generative AI models to produce ad copy, scripts, storyboards and simple motion graphics. It is seeded with brand guidelines, historical performance data and storytelling frameworks. The current implementation includes a `CreativeAgent` for creating text-based variants.

- **Optimization Engine**: Implements a baseline multi-armed bandit or reinforcement learning approach to choose between creative variants and allocate budget across channels. The `OptimizationAgent` analyses experiment results and recommends next tests based on the winning variant.

- **User Interface**: A web dashboard where marketers and creators can configure experiments, review generated creatives, approve assets, monitor performance and provide feedback. This is outside the scope of the current backend prototype.

- **Integration Layer**: Abstracts connections to advertising platforms, analytics providers and storage services. This layer makes it easy to add new channels or data sources without changing the core logic.

- **Compliance & Safety**: Handles content screening, privacy compliance and fairness auditing to ensure that generated content respects legal and ethical standards.

## Data Flow

1. A business snapshot is submitted via the API capturing products, audiences and historical performance.
2. The system generates an experiment plan, defining variants and metrics.
3. Creative variants are generated for each variant in the plan.
4. After running the experiment, the system collects results and computes the winning variant.
5. The optimization engine recommends new variants and next tests based on the results.

This modular design allows the project to focus on one component at a time during development while keeping the overall architecture extensible.
