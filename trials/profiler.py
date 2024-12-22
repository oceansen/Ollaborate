import sys
import time
import linecache

def trace_lines(frame, event, arg):
    """
    This function will be called whenever a new line of code is about to be executed.
    It captures the current timestamp, the filename, line number, and the actual code line.
    """
    if event == 'line':
        # Get human-readable timestamp
        current_time = time.strftime("%Y-%m-%d %H:%M:%S", time.localtime())

        # Get line info
        lineno = frame.f_lineno
        filename = frame.f_code.co_filename
        
        # Grab the actual line of code
        code_line = linecache.getline(filename, lineno).rstrip()

        # Print or log the information
        print(f"{current_time} - {filename}:{lineno} => {code_line}")

    return trace_lines


def main():
    # Your main program logic here
    
    # Simple example to demonstrate execution
    x = 10
    y = 20
    print(x + y)


if __name__ == "__main__":
    # Enable tracing
    sys.settrace(trace_lines)
    
    main()

    # Disable tracing if desired (to avoid tracing cleanup/shutdown code)
    sys.settrace(None)

