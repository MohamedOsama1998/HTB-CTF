#!/usr/bin/env python3

blocked_funcs = "pcntl_alarm,pcntl_fork,pcntl_waitpid,pcntl_wait,pcntl_wifexited,pcntl_wifstopped,pcntl_wifsignaled,pcntl_wifcontinued,pcntl_wexitstatus,pcntl_wtermsig,pcntl_wstopsig,pcntl_signal,pcntl_signal_get_handler,pcntl_signal_dispatch,pcntl_get_last_error,pcntl_strerror,pcntl_sigprocmask,pcntl_sigwaitinfo,pcntl_sigtimedwait,pcntl_exec,pcntl_getpriority,pcntl_setpriority,pcntl_async_signals,pcntl_unshare,error_log,system,exec,shell_exec,popen,passthru,link,symlink,syslog,ld,mail,stream_socket_sendto,dl,stream_socket_client,fsockopen".split(',')

def check_func(func):
	if func in blocked_funcs:
		print("BLOCKED!")
	else:
		print("CLEAR!")


if __name__ == "__main__":
	try:
		while True:
			in_func = input("Enter function:\n").lower()
			check_func(in_func)
	except KeyboardInterrupt:
		print("\nBye!")
		exit(0)