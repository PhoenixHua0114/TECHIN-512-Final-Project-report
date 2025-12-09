# CircuitPython Text Puzzle Game

A narrative-driven puzzle game for Xiao ESP32 with SSD1306 OLED display, rotary encoder, buttons, and accelerometer.

## Quick Start

1. **Build Hardware**: Connect all components according to pin connections table below
2. **Install CircuitPython**: Flash CircuitPython onto Xiao ESP32
3. **Copy Files**: Transfer all project files to `CIRCUITPY` drive
4. **Install Libraries**: Copy required libraries to `CIRCUITPY/lib/`
5. **Power On**: Connect battery and flip switch - game starts automatically
6. **Play**: Follow on-screen instructions, use buttons and tilt to navigate

## Hardware Requirements

- **Xiao ESP32** microcontroller
- **SSD1306 OLED** (128x64, I2C at address 0x3C)
- **ADXL345 Accelerometer** (I2C, shares bus with OLED)
- **Rotary Encoder** with built-in button
- **2x Push Buttons** (for navigation)
- **NeoPixel LED** (single WS2812B)
- **3.7V Battery** with on/off switch

### Pin Connections

| Component | ESP32 Pin |
|-----------|-----------|
| Rotary Encoder CLK | D0 |
| Rotary Encoder DT | D1 |
| Rotary Encoder Button | D9 |
| Left Button | D7 |
| Right Button | D8 |
| NeoPixel Data | D10 |
| I2C SDA | SDA |
| I2C SCL | SCL |

## Required CircuitPython Libraries

Copy these to your `CIRCUITPY/lib` folder:

- `adafruit_display_text`
- `adafruit_displayio_ssd1306`
- `adafruit_adxl34x`
- `adafruit_debouncer`
- `neopixel`
- `displayio`
- `i2cdisplaybus`

## Installation

1. Install CircuitPython on your Xiao ESP32
2. Copy all files from this directory to the `CIRCUITPY` drive
3. Install required libraries in `CIRCUITPY/lib/`
4. Reset the device

## File Structure

```
circuitpython_game/
├── code.py                 # Main entry point
├── game.py                 # Game orchestrator
├── display_manager.py      # OLED display control
├── input_manager.py        # Input device management
├── led_manager.py          # NeoPixel LED control
├── highscore_manager.py    # High score tracking
├── highscores.txt          # Saved high scores (auto-created)
├── rotary_encoder.py
├── lib
    ├── ...(All libaries used)
├── utils/
│   ├── __init__.py
│   ├── constants.py        # Configuration constants
│   └── filters.py          # Accelerometer filtering
└── chapters/
    ├── __init__.py
    ├── base_chapter.py     # Base class for chapters
    ├── chapter_01.py       # Chapter 1: Entering your memory
    ├── chapter_02.py       # Chapter 2: Toy box
    ├── chapter_03.py       # Chapter 3: Toy box?
    ├── chapter_04.py       # Chapter 4: Basement
    ├── chapter_05.py       # Chapter 5: Hospital
    ├── chapter_06.py       # Chapter 6: Your Path
    ├── chapter_07.py       # Chapter 7: Reflections
    ├── chapter_08.py       # Chapter 8: Flood
    ├── chapter_09.py       # Chapter 9: The Well
    └── chapter_10.py       # Chapter 10: Truth (ending)
```

## Components and Implementation

### Display Manager (`display_manager.py`)
- Controls SSD1306 OLED display (128x64 pixels) via I2C
- Renders text with automatic word wrapping and centering
- Manages display buffer and updates
- Uses `terminalio.FONT` for text rendering
- Handles multi-line text display with proper spacing

### Input Manager (`input_manager.py`)
- **Rotary Encoder**: Tracks position changes and button presses
- **Push Buttons**: Left/right navigation with debouncing (pull-up configuration)
- **ADXL345 Accelerometer**:
  - Calibrates on startup (1-second baseline measurement)
  - Detects tilt in all 6 directions (±X, ±Y, ±Z axes)
  - Detects sudden movement/taps using magnitude threshold
  - Uses exponential moving average filter for smooth readings
  - Configurable thresholds for different movement types
- **Choice Navigation**: Timeout-based menu system with visual countdown
- **Both Buttons Hold**: Requires simultaneous button press for specified duration

### LED Manager (`led_manager.py`)
- Controls single WS2812B NeoPixel LED
- **Color States**:
  - Yellow (255, 255, 0): Boot/startup
  - Blue (0, 0, 255): Correct choice
  - Red (255, 0, 0): Wrong choice
- Uses `auto_write=True` for immediate color updates
- Brightness set to 0.3 (30%) to conserve power

### Game Architecture (`game.py`)
- **Lazy Chapter Loading**: Chapters imported dynamically to save memory
- **Centralized LED Control**: Automatically displays appropriate LED based on chapter outcomes
  - Returns `"chapter_X"` → Blue LED (correct)
  - Returns `"restart_chapter_X"` → Red LED (wrong)
- **Aggressive Garbage Collection**: Runs `gc.collect()` multiple times between chapters
- **Module Unloading**: Removes completed chapters from `sys.modules` to free RAM
- **Shared I2C Bus**: Single I2C instance shared between display and accelerometer
- **Time Tracking**: Tracks completion time from Chapter 1 start to Chapter 10 end
- **High Score System**: Integrated high score tracking with persistent storage

### High Score Manager (`highscore_manager.py`)
- Tracks top 3 fastest completion times with player initials
- **Persistent Storage**: Saves to `highscores.txt` on flash memory (~60 bytes)
- **File Format**: Simple CSV format (INITIALS,TIME_SECONDS)
- **Automatic Ranking**: Sorts scores by completion time (fastest first)
- **Memory Efficient**: Only ~300-500 bytes RAM usage during operation
- **Initial Entry**: Uses rotary encoder to select 3-character initials
- **Display**: Shows high score board after game completion

### Chapter Base Class (`base_chapter.py`)
- Provides common helper methods for all chapters:
  - `show_narrative()`: Display text sequences with button press advancement
  - `handle_wrong_choice()`: Show failure message and trigger chapter restart
  - `handle_correct_choice()`: Show success message and progress to next chapter
  - `get_retry_count()`: Difficulty-based retry logic
  - `show_hint()`: Display contextual hints based on difficulty
- Each chapter inherits from `BaseChapter` and implements a `run()` method

### Memory Optimization
- Dynamic module loading/unloading prevents memory overflow
- Triple garbage collection calls at critical transition points
- Local variable cleanup with `del` before chapter transitions
- Minimal string allocations during gameplay
- Reuses display buffer without creating new objects

## How to Play

1. **Power On**: Press the **large push button**; NeoPixel light up with white, then turns yellow for 3 seconds, opening screen appears
2. **Select Difficulty**: Use rotary encoder to navigate, encoder button to confirm
3. **Navigate Game**:
   - Use **rotary encoder button** to advance narrative text
   - Use **left/right buttons** for multiple choice questions
   - **Tilt device** for movement-based challenges (forward, left, right, all directions)
   - **Double-tap display** when prompted (accelerometer detects taps)
   - **Hold both buttons** for certain challenges (must hold for required duration)
   - **Pattern matching** with left/right buttons (rhythm game in Chapter 5)
4. **Visual Feedback** (all LEDs display for 3 seconds):
   - **Blue LED**: Progressing to next chapter
   - **Red LED**: Restarting current chapter
   - **Yellow LED**: Boot/power on state
5. **After Completing Game**:
   - Game displays completion time
   - If top 3 fastest time: Enter 3 initials using rotary encoder
   - View high score board (top 3 times)
   - Option to restart: Returns to difficulty selection (opening screen only shown once)

## Game Flow

The game consists of 10 chapters with different challenges:

- **Chapter 1 - Entering Your Memory**: Navigate to correct door using left/right buttons with time limit
- **Chapter 2 - Toy Box**: Detect X and Y axis movement, then choose the correct action with photo album
- **Chapter 3 - Toy Box?**: Tilt device left, hold both buttons for duration, make timed choice
- **Chapter 4 - Basement**: Tilt forward down stairs, answer reflection question, double-tap to wake up
- **Chapter 5 - Hospital**: Match rhythm patterns (L/R button sequences), then tilt forward to run from darkness
- **Chapter 6 - Your Path**: Select correct elevator floor number, no retries
- **Chapter 7 - Reflections**: Move device in all 4 directions (X/Y axes), then wave correct hand to mirror shadow
- **Chapter 8 - Flood**: Hold both buttons to grab edge, double-tap to knock on door
- **Chapter 9 - The Well**: Tilt forward to lean down, hold both buttons to pull rope
- **Chapter 10 - Truth**: The paradox ending - discover the truth about your past (wait and observe)

## Difficulty Levels

- **Easy**: More hints, longer timeouts, more retry chances
- **Medium**: Balanced difficulty
- **Hard**: Minimal hints, shorter timeouts, fewer retries

## Story Synopsis

You wake up in a fog, exploring fragmented memories. Through various challenges, you discover the truth about a tragic event involving your brother and a well. The game explores themes of memory, guilt, and acceptance.

## High Score System

The game tracks the top 3 fastest completion times with persistent storage:

### How It Works
1. **Timer starts** when Chapter 1 begins
2. **Timer stops** when Chapter 10 completes
3. **Completion time** is calculated in seconds
4. **Ranking check**: If your time is in top 3, you achieved a high score!

### Entering Your Initials
If you achieve a high score:
- Display shows "NEW HIGH SCORE! Rank #X"
- **Initial Entry Screen** appears with format: `[A] A  A`
- **Controls**:
  - **Rotary encoder**: Cycle through letters A-Z at current position
  - **Left/Right buttons**: Move between the 3 initial positions
  - **Encoder button**: Confirm and finish (no flashing screen)
- Navigate between positions and set each letter, then press encoder to save

### High Score Display
After every game completion:
- Shows high score board with top 3 times
- Format: `#1 ABC 12:34` (rank, initials, time in MM:SS)
- Each score displays for 3 seconds
- Press encoder button to advance faster

### Data Storage
- Saved to `highscores.txt` on flash memory
- File format: `INITIALS,TIME_SECONDS` (one per line)
- Automatically created on first high score
- Uses only ~60 bytes of flash storage
- Persists across power cycles
- **No SD card required** - all data stored on microcontroller

### Memory Impact
- **Flash Storage**: 60 bytes (negligible - 0.003% of available space)
- **RAM Usage**: ~300-500 bytes peak during high score operations
- **Performance**: Zero impact on gameplay (file I/O only at game end)

## Troubleshooting

### Display not working
- Check I2C connections
- Verify OLED address is 0x3C in `utils/constants.py`

### Accelerometer not responding
- Ensure ADXL345 is connected to I2C bus
- Check calibration at startup

### Buttons not working
- Verify pin connections in `utils/constants.py`
- Check pull-up resistors are enabled

### Memory errors
- CircuitPython has limited RAM
- Try reducing font size or text length if needed

## Technical Features

### Centralized LED System
The game uses a centralized LED control system in `game.py` that automatically handles visual feedback:
- Chapters return simple strings: `"chapter_X"` for success or `"restart_chapter_X"` for failure
- The game loop automatically detects these return values and triggers appropriate LED colors
- No need to manually call LED methods in individual chapter files
- All LEDs automatically turn off after 3 seconds

### Accelerometer Filtering
The game uses exponential moving average (EMA) filtering to smooth accelerometer readings:
- Alpha value of 0.3 balances responsiveness and stability
- Baseline calibration on startup compensates for device orientation
- Separate thresholds for tilt detection vs. tap/movement detection

### Memory Management
CircuitPython has limited RAM (~200KB available), requiring aggressive memory optimization:
- Chapters are loaded one at a time and unloaded after completion
- `gc.collect()` called 3 times at transitions to clear circular references
- Local variables explicitly deleted before chapter transitions
- String constants reused where possible

### Input Debouncing
All physical inputs use debouncing to prevent false triggers:
- Rotary encoder tracks position changes without double-counting
- Button presses use pull-up resistors with software debouncing
- 0.15-second delay after button press in rhythm game prevents double-detection

## Customization

### Pin Configuration
Edit `utils/constants.py` to change pin assignments:
```python
ENCODER_CLK = board.D0
ENCODER_DT = board.D1
ENCODER_BUTTON = board.D9
LEFT_BUTTON_PIN = board.D7
RIGHT_BUTTON_PIN = board.D8
NEOPIXEL_PIN = board.D10
```

### Movement Thresholds
Adjust sensitivity in `utils/constants.py`:
```python
TILT_THRESHOLD = 2.5          # Degrees for tilt detection
MOVEMENT_THRESHOLD = 1.5      # G-force for movement
TAP_THRESHOLD = 20.0          # G-force for tap/shake
```

### LED Colors
Change color scheme in `utils/constants.py`:
```python
COLOR_BOOT = (255, 255, 0)    # Yellow (R, G, B)
COLOR_CORRECT = (0, 0, 255)   # Blue
COLOR_WRONG = (255, 0, 0)     # Red
```

### Display Settings
Modify `utils/constants.py` for display configuration:
```python
DISPLAY_WIDTH = 128
DISPLAY_HEIGHT = 64
DISPLAY_ADDRESS = 0x3C        # I2C address
```

## Enclosure Design
- The idea of the enclosure is a simple white box, where we can treat is as the place we store the memory
- There are some paintings and textures on the box's surface, indicating important pieces of the memory

## Credits

- Game Design: Phoenix Hua
- Insturctors: Haonan Peng, Zubin
- Implementation: CircuitPython + Claude Code

Enjoy the journey through memories!
