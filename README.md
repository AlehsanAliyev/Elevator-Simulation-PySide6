# Elevator Simulation (PySide6 + pygame)

A single-window desktop app that embeds a pygame-rendered elevator simulation directly inside a Qt UI.
Qt owns the event loop, keeping the interface responsive while the simulation runs offscreen.

## Features
- Embedded simulation panel rendered from an offscreen pygame Surface
- Responsive Qt UI with status, controls, and event logging
- Scheduler modes: Simple, FIFO, and SCAN
- Door state machine with open/close commands and emergency stop
- Testable core logic (no Qt or pygame dependency)

## Run on Windows
```powershell
python -m venv .venv
.\.venv\Scripts\Activate.ps1
pip install -r requirements.txt
$env:PYTHONPATH = "src"
python -m elevator_sim
```

## Run Tests
```powershell
python -m pytest
```

## Architecture
```
Qt UI (PySide6)
  -> QTimer tick
  -> Controller.update(dt)
  -> Renderer.draw(surface)
  -> QLabel pixmap

core/ (pure Python) : model, scheduler, controller, events
render/             : pygame offscreen drawing -> QImage
ui/                 : .ui files + wiring
```

## Design Notes
- Qt owns the main loop; no blocking while-loops in the UI thread.
- pygame is only used for offscreen rendering (no display window).
- Emergency stop freezes movement and door transitions until cleared.
