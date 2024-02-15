import locale

# The test fixtures can break if the locale is non-US.
locale.setlocale(locale.LC_ALL, 'en_US.UTF-8')
