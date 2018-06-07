class CLIExceptionBase(Exception): pass


class ConfigurationError(CLIExceptionBase): pass


class IncompleteAccountInfoError(ConfigurationError): pass
