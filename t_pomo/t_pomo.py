import curses
import time

from art import text2art


def _get_hh_mm_ss(seconds: int) -> str:
    """Convert second to HH:MM:ss format."""
    hour, left_sec = divmod(seconds, 3600)
    minute, second = divmod(left_sec, 60)

    return f"{hour:02}:{minute:02}:{second:02}"


def _show_countdown_info(
    stdscr: curses.window,
    countdown_seconds: int = 25 * 60,
    message: str = "",
) -> None:
    curses.start_color()
    curses.init_pair(1, curses.COLOR_CYAN, curses.COLOR_BLACK)

    tomato_length = (
        max(map(len, text2art("00:00:00", font="soft", space=0).split("\n"))) // 2
    )

    start_time = time.monotonic()

    for second in range(countdown_seconds, 0, -1):
        stdscr.clear()
        stdscr.addstr(1, 0, "🍅" * tomato_length)
        stdscr.attron(curses.color_pair(1))
        stdscr.addstr(2, 0, text2art(f"{_get_hh_mm_ss(second)}", font="soft", space=0))
        stdscr.attroff(curses.color_pair(1))
        stdscr.addstr(9, 0, "🍅" * tomato_length)
        stdscr.addstr(11, 0, text2art(message))
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
        )
        _show_countdown_info(
            stdscr=stdscr,
            countdown_seconds=break_seconds,
            message=f"BREAK [{loop} / {loop_time}]",
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
