"""PyCharm entry point for the self-contained Necker Studio folder."""

if __package__:
    from .gui import main
else:
    from gui import main


if __name__ == "__main__":
    main()
