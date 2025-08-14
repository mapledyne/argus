"""Custom handlers for the diagnostics logging system."""

import logging


class JSONFileHandler(logging.FileHandler):
    """Custom file handler that writes logs as a single JSON array."""

    def __init__(self, filename, mode='a', encoding=None, delay=False):
        super().__init__(filename, mode, encoding, delay)
        self.log_entries = []
        self.state_entries = []
        self._initialize_file()

    def _initialize_file(self):
        """Initialize the JSON file with opening bracket."""
        if self.stream is None:
            self.stream = self._open()
        # Only write the opening structure if the file is empty
        if self.stream.tell() == 0:
            self.stream.write('{"logs": [\n')
            self.stream.flush()

    def emit(self, record):
        """Emit a record as JSON array element."""
        try:
            if not self.stream:
                # Try to reinitialize the stream if it's None
                self._initialize_file()

            msg = self.format(record)
            if self.log_entries:  # Add comma for all but first entry
                self.stream.write(',\n')
            self.stream.write(msg)
            self.stream.flush()
            self.log_entries.append(record)
        except Exception:   # pylint: disable=broad-exception-caught
            self.handleError(record)

    def close(self):
        """Close the handler and complete the JSON array."""
        if self.stream:
            self.stream.write('],\n')
            self.stream.write('"state": [\n')
            for i, state_entry in enumerate(self.state_entries):
                if i < len(self.state_entries) - 1:
                    self.stream.write(f'{state_entry},\n')
                else:
                    self.stream.write(f'{state_entry}\n')
            self.stream.write('],\n"diagnostics_state": ')
            # Import at runtime to avoid circular imports
            from log_functions import _diagnostics_state  # pylint: disable=C0415
            self.stream.write(f'{_diagnostics_state()}')
            self.stream.write('\n}')
            self.stream.flush()
            super().close()
