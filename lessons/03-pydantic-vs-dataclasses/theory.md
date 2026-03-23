## The ultimate dataclass

After the previous lesson, you might have gotten an impression that Pydantic models are just better dataclasses. Easier
strict typing, powerful validators, de/serialization support - and they both generally serve the same purpose: to carry
data between parts of your application.

But Pydantic is not just an ultimate dataclass. In a real project, Pydantic models _complement_ dataclasses, not replace
them.

What exactly are their respective use cases?