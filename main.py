"""PyCharm entry point for Nicholas's Nice Necker Cube Experiment."""

if __package__:
    from .gui import main
else:
    from gui import main


if __name__ == "__main__":
    main()
