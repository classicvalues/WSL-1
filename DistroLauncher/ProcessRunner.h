#pragma once
// Wraps up Win32 API's into an run-once-and-discard object
// to launch an external process and capture its outputs.
// Once created it cannot be reassigned, nor reused,
// except for holding exit code and std out and err streams content
// of the launched process.
namespace Helpers {
    class ProcessRunner {
    private:
        // Exposed thru getters.
        std::wstring cmd;
        DWORD exit_code;
        std::wstring stdOut;
        std::wstring stdErr;
        bool defunct;
        bool alreadyRun;

        // internals. Could be hidden by PIMPL, for instance,
        // but that's not necessary for now.
        HANDLE g_hChildStd_OUT_Rd = NULL;
        HANDLE g_hChildStd_OUT_Wr = NULL;
        HANDLE g_hChildStd_ERR_Rd = NULL;
        HANDLE g_hChildStd_ERR_Wr = NULL;
        SECURITY_ATTRIBUTES _sa;
        PROCESS_INFORMATION _piProcInfo;
        STARTUPINFO _siStartInfo;

        void read_pipes();
        void setDefunctState();

    public:
        // Constructs a runner for a given CLI.
        // Once constructed, it cannot have its CLI argument changed.
        ProcessRunner(std::wstring_view commandLine);

        // Non-copyable, but movable.
        ProcessRunner(const ProcessRunner& other) = delete;
        ProcessRunner& operator=(const ProcessRunner& other) = delete;
        ProcessRunner(ProcessRunner&& other) = default;
        ProcessRunner& operator=(ProcessRunner&& other) = default;

        // The runner is considered defunct if it fails to construct the pipe
        // which will conduct the standard streams.
        // This is a way to avoid the need for exceptions.
        bool isDefunct();

        // Runs the CLI given to constructor and returns it's exit code.
        // If called more than once, returns the cached exit code.
        // Never tries to run the command a second time.
        DWORD run();

        // Returns the cached exit code.
        DWORD getExitCode();

        // Returns a view of the process standard output stream.
        std::wstring_view getStdOut();

        // Returns a view of the process standard error stream.
        std::wstring_view getStdErr();

        ~ProcessRunner();
    };
}