from dataclasses import dataclass, asdict, field

@dataclass(init=True, repr=True)
class UsedRule(object):
    layer: int
    branch: str
    rule: str
    context: dict = field(default_factory=dict)
    decisions: dict = field(default_factory=dict)

    def to_dict(self):
        return asdict(self)