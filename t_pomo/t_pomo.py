import curses
import time
from collections.abc import Callable
from typing import Optional

from art import text2art

try:
    import inspirational_quotes
except Exception:  # pragma: no cover - optional dependency
    inspirational_quotes = None

FONT = "soft"
QUOTE_STR = (
    inspirational_quotes.quote().get("quote", "")
    if inspirational_quotes is not None
    else ""
)
MIN_TERMINAL_WIDTH = 80
MIN_TERMINAL_HEIGHT = 24
CONTROL_INSTRUCTION = "[p] PAUSE | [s] SKIP | [q] STOP"


def _add_centered_segments(
    stdscr: curses.window,
    y: int,
    segments: list[tuple[str, int]],
) -> None:
    """Safely draw colored text segments centered on a terminal row."""
    max_y, max_x = stdscr.getmaxyx()
    if y < 0 or y >= max_y or max_x <= 0:
        return

    total_length = sum(len(text) for text, _ in segments)
    x = max(0, (max_x - total_length) // 2)

    for text, attribute in segments:
        if x >= max_x:
            break

        available_width = max_x - x
        # Writing the bottom-right cell can raise curses.error on some terminals.
        if y == max_y - 1:
            available_width -= 1
        visible_text = text[: max(0, available_width)]
        if not visible_text:
            break

        try:
            stdscr.addstr(y, x, visible_text, attribute)
        except curses.error:
            pass
        x += len(visible_text)


def _display_terminal_too_small(
    stdscr: curses.window,
    required_width: int,
    required_height: int,
) -> None:
    """Show the current and required terminal dimensions."""
    current_height, current_width = stdscr.getmaxyx()
    normal = curses.A_NORMAL
    good = curses.color_pair(1) | curses.A_BOLD
    bad = curses.color_pair(3) | curses.A_BOLD
    start_y = max(0, (current_height - 5) // 2)

    stdscr.erase()
    _add_centered_segments(
        stdscr,
        start_y,
        [("Terminal size too small:", curses.A_BOLD)],
    )
    _add_centered_segments(
        stdscr,
        start_y + 1,
        [
            ("Width = ", normal),
            (str(current_width), good if current_width >= required_width else bad),
            (" Height = ", normal),
            (str(current_height), good if current_height >= required_height else bad),
        ],
    )
    _add_centered_segments(
        stdscr,
        start_y + 3,
        [("Needed for current config:", curses.A_BOLD)],
    )
    _add_centered_segments(
        stdscr,
        start_y + 4,
        [
            (f"Width = {required_width} Height = {required_height}", normal),
        ],
    )
    stdscr.refresh()


def _wait_for_usable_terminal(
    stdscr: curses.window,
    required_width: int,
    required_height: int,
) -> tuple[float, bool]:
    """Wait for a usable terminal, returning paused seconds and whether to stop."""
    wait_started_at: Optional[float] = None

    while True:
        current_height, current_width = stdscr.getmaxyx()
        if (
            current_width >= required_width
            and current_height >= required_height
        ):
            stdscr.timeout(-1)
            waited = (
                0.0
                if wait_started_at is None
                else time.monotonic() - wait_started_at
            )
            return waited, False

        if wait_started_at is None:
            wait_started_at = time.monotonic()

        _display_terminal_too_small(
            stdscr,
            required_width=required_width,
            required_height=required_height,
        )
        stdscr.timeout(100)
        if stdscr.getch() == ord("q"):
            stdscr.timeout(-1)
            return time.monotonic() - wait_started_at, True


def _get_hh_mm_ss(seconds: int) -> str:
    """Convert second to HH:MM:ss format."""
    hour, left_sec = divmod(seconds, 3600)
    minute, second = divmod(left_sec, 60)

    return f"{hour:02}:{minute:02}:{second:02}"


def _show_art_text_with_addstr_coordinate(
    stdscr: curses.window, y: int, x: int, art_text_str: str
) -> None:
    """
    Display ASCII art text on the curses window at specified coordinates.

    Args:
        stdscr (curses.window): The curses window object where the text will be displayed.
        y (int): The y-coordinate (row) where the text will start.
        x (int): The x-coordinate (column) where the text will start.
        art_text_str (str): The ASCII art text to be displayed.

    Returns:
        None
    """
    art_text_row_list = art_text_str.split("\n")
    for i, art_text_row in enumerate(art_text_row_list):
        stdscr.addstr(y + i, x, art_text_row)


def _display_countdown_clock(
    stdscr: curses.window,
    second: int,
    countdown_seconds: int,
    timer_x: int,
    message_x: int,
    message_art_text: str,
    bar_length: int,
    color_pair: int,
) -> None:
    """Render the countdown timer and progress bar."""

    # Calculate progress (1.0 to 0.0) - Time Remaining
    progress = second / countdown_seconds
    filled_length = int(bar_length * progress)
    
    stdscr.clear()
    
    # Draw the progress bar (Top)
    # Filled part: Reverse video spaces (looks like solid blocks)
    stdscr.attron(curses.color_pair(color_pair) | curses.A_REVERSE)
    stdscr.addstr(1, timer_x, " " * filled_length)
    stdscr.attroff(curses.color_pair(color_pair) | curses.A_REVERSE)
    
    # Empty part: Hyphens
    stdscr.addstr(1, timer_x + filled_length, "-" * (bar_length - filled_length))

    stdscr.attron(curses.color_pair(color_pair))
    _show_art_text_with_addstr_coordinate(
        stdscr=stdscr,
        y=2,
        x=timer_x,
        art_text_str=text2art(f"{_get_hh_mm_ss(second)}", font=FONT, space=1),
    )
    stdscr.attroff(curses.color_pair(color_pair))
    
    # Draw the progress bar (Bottom)
    stdscr.attron(curses.color_pair(color_pair) | curses.A_REVERSE)
    stdscr.addstr(9, timer_x, " " * filled_length)
    stdscr.attroff(curses.color_pair(color_pair) | curses.A_REVERSE)
    stdscr.addstr(9, timer_x + filled_length, "-" * (bar_length - filled_length))
    _show_art_text_with_addstr_coordinate(
        stdscr=stdscr,
        y=11,
        x=message_x - 1,
        art_text_str=message_art_text,
    )
    stdscr.refresh()


def _show_inspirational_quote(stdscr: curses.window, width: int) -> None:
    """Display an inspirational quote centered on the screen."""
    max_y, max_x = stdscr.getmaxyx()
    y = 19
    
    if y >= max_y:
        return  # Screen too short

    quote = QUOTE_STR
    if len(quote) > width:
        quote = quote[:width-1]
    
    x = max(0, (width - len(quote)) // 2)
    
    try:
        stdscr.addstr(y, x, quote)
    except curses.error:
        pass  # Ignore drawing errors for the quote


def _handle_pause(
    stdscr: curses.window,
    paused: bool,
    start_time: float,
    required_width: int,
    required_height: int,
    redraw: Callable[[], None],
) -> tuple[bool, float, bool, bool]:
    """Handle pause, skip, and quit commands, showing control instructions."""

    def finish(stop: bool = False, skip: bool = False) -> tuple[bool, float, bool, bool]:
        stdscr.nodelay(False)
        return paused, start_time, stop, skip

    waited, stop = _wait_for_usable_terminal(
        stdscr,
        required_width=required_width,
        required_height=required_height,
    )
    start_time += waited
    if stop:
        return finish(stop=True)
    if waited:
        redraw()

    width = stdscr.getmaxyx()[1]
    instruction = (
        "[p] RESUME | [s] SKIP | [q] STOP"
        if paused
        else CONTROL_INSTRUCTION
    )
    stdscr.addstr(21, (width - len(instruction)) // 2, instruction)
    stdscr.nodelay(True)
    key = stdscr.getch()
    if key == ord("q"):
        return finish(stop=True)
    if key == ord("s"):
        return finish(skip=True)
    if key == ord("p"):
        paused = not paused

    while paused:
        waited, stop = _wait_for_usable_terminal(
            stdscr,
            required_width=required_width,
            required_height=required_height,
        )
        start_time += waited
        if stop:
            return finish(stop=True)
        if waited:
            redraw()

        width = stdscr.getmaxyx()[1]
        resume_instruction = "[p] RESUME | [s] SKIP | [q] STOP"
        stdscr.addstr(
            21,
            (width - len(resume_instruction)) // 2,
            resume_instruction,
        )
        stdscr.nodelay(True)
        key = stdscr.getch()
        if key == ord("q"):
            return finish(stop=True)
        if key == ord("s"):
            return finish(skip=True)
        if key == ord("p"):
            paused = False
        time.sleep(0.1)
        start_time += 0.1

    return finish()


def _show_countdown_info(
    stdscr: curses.window,
    countdown_seconds: int = 25 * 60,
    message: str = "",
    is_working: bool = True,
) -> bool:
    curses.start_color()
    curses.use_default_colors()
    curses.init_pair(1, curses.COLOR_CYAN, -1)
    curses.init_pair(2, curses.COLOR_YELLOW, -1)
    curses.init_pair(3, curses.COLOR_RED, -1)

    message_art_text = text2art(message, font=FONT, space=0)
    max_timer_row_len = max(
        map(len, text2art("00:00:00", font=FONT, space=1).split("\n"))
    )
    max_message_row_len = max(map(len, message_art_text.split("\n")))
    bar_length = max_timer_row_len
    required_width = max(
        MIN_TERMINAL_WIDTH,
        max_timer_row_len + 2,
        max_message_row_len + 2,
        len(CONTROL_INSTRUCTION),
    )
    required_height = MIN_TERMINAL_HEIGHT

    curses.curs_set(0)  # Hide cursor
    start_time = time.monotonic()

    paused = False
    for second in range(countdown_seconds, 0, -1):
        # Determine color based on time remaining
        progress = second / countdown_seconds
        if progress > 0.5:
            color_pair = 1  # Cyan
        elif progress > 0.2:
            color_pair = 2  # Yellow
        else:
            color_pair = 3  # Red

        waited, stop = _wait_for_usable_terminal(
            stdscr,
            required_width=required_width,
            required_height=required_height,
        )
        start_time += waited
        if stop:
            return True

        def redraw() -> None:
            _, current_width = stdscr.getmaxyx()
            _display_countdown_clock(
                stdscr=stdscr,
                second=second,
                countdown_seconds=countdown_seconds,
                timer_x=(current_width - max_timer_row_len) // 2,
                message_x=(current_width - max_message_row_len) // 2,
                message_art_text=message_art_text,
                bar_length=bar_length,
                color_pair=color_pair,
            )
            _show_inspirational_quote(stdscr, current_width)

        redraw()

        paused, start_time, stop, skip = _handle_pause(
            stdscr=stdscr,
            paused=paused,
            start_time=start_time,
            required_width=required_width,
            required_height=required_height,
            redraw=redraw,
        )

        if stop:
            return True
        if skip:
            return False

        next_time = start_time + 1
        time.sleep(max(0, next_time - time.monotonic()))
        start_time = next_time

    return False


def count_down(
    stdscr: curses.window,
    work_seconds: int = 25 * 60,
    break_seconds: int = 5 * 60,
    loop_time: int = 1,
) -> None:
    for loop in range(loop_time):
        if _show_countdown_info(
            stdscr=stdscr,
            countdown_seconds=work_seconds,
            message=f"WORK[{loop}/{loop_time}]",
            is_working=True,
        ):
            return
        if _show_countdown_info(
            stdscr=stdscr,
            countdown_seconds=break_seconds,
            message=f"BREAK[{loop}/{loop_time}]",
            is_working=False,
        ):
            return

    stdscr.getch()  # Wait for key press


def main() -> None:
    try:
        work_seconds = (
            int(input("Enter working time in minutes [25]: ").strip() or "25") * 60
        )
        break_seconds = int(input("Enter break time in minutes [5]: ").strip() or "5") * 60
        pomo_loop_time = int(input("Enter countdown loop time [1]: ").strip() or "1")

        curses.wrapper(
            count_down,
            work_seconds,
            break_seconds,
            pomo_loop_time,
        )
    except Exception as e:
        with open("t_pomo_error.log", "w") as f:
            import traceback
            traceback.print_exc(file=f)
        print(f"An error occurred. Check t_pomo_error.log for details.\n{e}")


if __name__ == "__main__":
    main()
