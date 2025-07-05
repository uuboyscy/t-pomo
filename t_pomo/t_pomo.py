import curses
import time

from art import text2art

try:
    import inspirational_quotes
except Exception:  # pragma: no cover - optional dependency
    inspirational_quotes = None

FONT = "soft"
QUOTE_STR = inspirational_quotes.quote().get("quote", "")


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
    emoji: str,
    emoji_length: int,
) -> None:
    """Render the countdown timer and progress bar."""

    complete_progress_emoji_length = int(
        emoji_length * (second / countdown_seconds)
    )
    emoji_line = (
        emoji * (emoji_length - complete_progress_emoji_length)
        + "🍀" * complete_progress_emoji_length
    )

    stdscr.clear()

    stdscr.addstr(1, timer_x - 2, emoji_line)
    stdscr.attron(curses.color_pair(1))
    _show_art_text_with_addstr_coordinate(
        stdscr=stdscr,
        y=2,
        x=timer_x,
        art_text_str=text2art(f"{_get_hh_mm_ss(second)}", font=FONT, space=1),
    )
    stdscr.attroff(curses.color_pair(1))
    stdscr.addstr(9, timer_x - 2, emoji_line)
    _show_art_text_with_addstr_coordinate(
        stdscr=stdscr,
        y=11,
        x=message_x - 1,
        art_text_str=message_art_text,
    )
    stdscr.refresh()


def _show_inspirational_quote(stdscr: curses.window, width: int) -> None:
    """Display an inspirational quote centered on the screen."""
    stdscr.addstr(19, (width - len(QUOTE_STR)) // 2, QUOTE_STR)


def _handle_pause(
    stdscr: curses.window, paused: bool, width: int, start_time: float
) -> tuple[bool, float, bool]:
    """Handle pause state, quit command and show instructions."""

    instruction = "[Press 'p' to resume]" if paused else "[Press 'p' to pause]"
    stdscr.addstr(21, (width - len(instruction)) // 2, instruction)
    stdscr.nodelay(True)
    key = stdscr.getch()
    if key == ord("q"):
        return paused, start_time, True
    if key == ord("p"):
        paused = not paused

    while paused:
        stdscr.addstr(
            21,
            (width - len("[Press 'p' to resume]")) // 2,
            "[Press 'p' to resume]",
        )
        key = stdscr.getch()
        if key == ord("q"):
            return paused, start_time, True
        if key == ord("p"):
            paused = False
        time.sleep(0.1)
        start_time += 0.1

    stdscr.nodelay(False)
    return paused, start_time, False


def _show_countdown_info(
    stdscr: curses.window,
    countdown_seconds: int = 25 * 60,
    message: str = "",
    is_working: bool = True,
) -> None:
    curses.start_color()
    curses.init_pair(1, curses.COLOR_CYAN, curses.COLOR_BLACK)

    message_art_text = text2art(message, font=FONT, space=0)
    max_timer_row_len = max(
        map(len, text2art("00:00:00", font=FONT, space=1).split("\n"))
    )
    max_message_row_len = max(map(len, message_art_text.split("\n")))
    emoji_length = max_timer_row_len // 2

    emoji = "🍅" if is_working else "🍵"

    start_time = time.monotonic()

    paused = False
    for second in range(countdown_seconds, 0, -1):
        _, max_curses_width = stdscr.getmaxyx()
        timer_text_start_x = (max_curses_width - max_timer_row_len) // 2
        message_text_start_x = (max_curses_width - max_message_row_len) // 2

        _display_countdown_clock(
            stdscr=stdscr,
            second=second,
            countdown_seconds=countdown_seconds,
            timer_x=timer_text_start_x,
            message_x=message_text_start_x,
            message_art_text=message_art_text,
            emoji=emoji,
            emoji_length=emoji_length,
        )

        _show_inspirational_quote(stdscr, max_curses_width)

        paused, start_time, stop = _handle_pause(
            stdscr=stdscr,
            paused=paused,
            width=max_curses_width,
            start_time=start_time,
        )

        if stop:
            return True

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


if __name__ == "__main__":
    main()
