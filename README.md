# Argus - Simple Logging Made for a Simple Person (me)

I start many projects wanting to log things well, but often started with just
print statements since they're just so easy. Then I'd hit some bug and instead
of backing up, just add more and more print statements until I sorted the
problem out, invariably forgetting to remove one somewhere, later.

I needed something better so I'd get around to adding logging at the begging
instead of halfway through once I'd been bitten. But I know myself, so it had
to be "almost as easy as just print()".

And thus Argus was born. It started out as basically just a quick auto-config
of the logging system to now it can automatically log both to console
(in color!) and to structured log files all without adding any code beside
the starting import.

```python
import argus
argus.debug("Why did this fail here?")
argus.error("Total bummer of an error: widget=$widget", widget=value)
```

A handful of config options are available, the most important of which can be
set via environment variables so you can get the style and levels of logging
you want without additional code overhead.

## Install

Install using pip if you want to try it:
```
pip install argus-logging
```

Full documentation with the logging commands, function decorators, and
config options here: [Argus-logging full documentation](https://mapledyne.github.io/argus-logging/)
