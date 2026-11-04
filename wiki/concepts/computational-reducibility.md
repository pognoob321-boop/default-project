---
type: concept
updated: 2026-07-22
---

# Computational Reducibility

The property of a computational process where shortcuts exist—meaning the outcome can be determined without running every intermediate step. A system is computationally reducible if there exists a faster algorithm that produces the same result in fewer steps than the system's own evolution. Examples include periodic or nested patterns in cellular automata, where formulas or auxiliary computations can predict the state after *t* steps in O(log *t*) time rather than O(*t*). Computational reducibility is the exception rather than the rule: most non-trivial systems are computationally irreducible. Identifying reducible subsystems within otherwise irreducible systems (via coarse-graining or statistical approximation) is a key strategy for making predictions about complex phenomena.

## Related

- [Computational Irreducibility](computational-irreducibility.md)
- [Kolmogorov Complexity](kolmogorov-complexity.md)
- [Computational Irreducibility Research](../research/computational-irreducibility.md)
