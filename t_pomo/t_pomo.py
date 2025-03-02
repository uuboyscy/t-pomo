import curses
import time

from art import text2art


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


def _show_countdown_info(
    stdscr: curses.window,
    countdown_seconds: int = 25 * 60,
    message: str = "",
    is_working: bool = True,
) -> None:
    curses.start_color()
    curses.init_pair(1, curses.COLOR_CYAN, curses.COLOR_BLACK)

    timer_text = text2art("00:00:00", font="soft", space=0)
    max_timer_row_len = max(map(len, timer_text.split("\n")))
    emoji_length = max_timer_row_len // 2

    emoji = "🍅" if is_working else "🍵"

    start_time = time.monotonic()

    for second in range(countdown_seconds, 0, -1):
        _, max_curses_width = stdscr.getmaxyx()
        msg_start_x = (max_curses_width - max_timer_row_len) // 2

        complete_progress_emoji_length = int(
            emoji_length * (second / countdown_seconds),
        )
        emoji_line = (
            emoji * (emoji_length - complete_progress_emoji_length)
            + "🍀" * complete_progress_emoji_length
        )

        stdscr.clear()

        stdscr.addstr(1, msg_start_x - 2, emoji_line)

        stdscr.attron(curses.color_pair(1))
        _show_art_text_with_addstr_coordinate(
            stdscr=stdscr,
            y=2,
            x=msg_start_x,
            art_text_str=text2art(f"{_get_hh_mm_ss(second)}", font="soft", space=0),
        )
        stdscr.attroff(curses.color_pair(1))

        stdscr.addstr(9, msg_start_x - 2, emoji_line)

        _show_art_text_with_addstr_coordinate(
            stdscr=stdscr,
            y=11,
            x=msg_start_x,
            art_text_str=text2art(message),
        )

        stdscr.refresh()

        next_time = start_time + 1
        time.sleep(max(0, next_time - time.monotonic()))
        start_time = next_time


def count_down(
    stdscr: curses.window,
    work_seconds: int = 25 * 60,
    break_seconds: int = 5 * 60,
    loop_time: int = 1,
) -> None:
    for loop in range(loop_time):
        _show_countdown_info(
            stdscr=stdscr,
            countdown_seconds=work_seconds,
            message=f"WORK [{loop} / {loop_time}]",
            is_working=True,
        )
        _show_countdown_info(
            stdscr=stdscr,
            countdown_seconds=break_seconds,
            message=f"BREAK [{loop} / {loop_time}]",
            is_working=False,
        )

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
