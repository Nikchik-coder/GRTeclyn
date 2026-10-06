/* GRTeclyn
 * Copyright 2022 The GRTL collaboration.
 * Please refer to LICENSE in GRTeclyn's root directory.
 */

#ifndef CHECKPOINTRETENTION_HPP_
#define CHECKPOINTRETENTION_HPP_

#include <AMReX_ParallelDescriptor.H>
#include <AMReX_Print.H>

#include <algorithm>
#include <cstdint>
#include <filesystem>
#include <string>
#include <system_error>
#include <utility>
#include <vector>

/* Rolling retention of restart checkpoints.

   A checkpoint of this merger is ~10 GB, and a long run writing one every few
   code units fills a scratch disk long before it reaches its stop time.  The
   only checkpoints anyone ever restarts from are the newest ones, so keep a
   fixed number of them and drop the rest, right after a new one lands.

   Order matters for safety: the prune runs AFTER amrex::Amr::checkPoint()
   returns, so the newest checkpoint is complete on disk before any older one
   is removed.  A run killed mid-write therefore still has its previous
   checkpoint -- the delete is never reached.  Two further guards:

   - a directory is a deletion candidate only if it holds a `Header`, so a
     checkpoint another process is still writing is never half-removed;
   - the checkpoint this run restarted from is never deleted, even if it
     happens to sit in the same directory under the same prefix.

   Scope is the run's own `check_file` prefix, so a co-tenant's checkpoints on
   the same disk are not candidates.  Default off (`checkpoint_keep = 0` keeps
   everything): no archived run changes behaviour.
*/
namespace CheckpointRetention
{

//! Keep the `a_keep` newest checkpoints written under `a_check_file_root`,
//! delete the rest.  `a_keep <= 0` disables the prune entirely.
//! `a_protect_path` (may be empty) is never deleted.
inline void prune(const std::string &a_check_file_root, int a_keep,
                  const std::string &a_protect_path)
{
    if (a_keep <= 0)
    {
        return;
    }
    if (!amrex::ParallelDescriptor::IOProcessor())
    {
        return;
    }

    namespace fs = std::filesystem;

    const fs::path root{a_check_file_root};
    const std::string prefix = root.filename().string();
    if (prefix.empty())
    {
        return;
    }
    const fs::path dir =
        root.has_parent_path() ? root.parent_path() : fs::path{"."};

    std::error_code ec;
    if (!fs::is_directory(dir, ec))
    {
        return;
    }

    fs::path protect;
    if (!a_protect_path.empty())
    {
        protect = fs::weakly_canonical(fs::path{a_protect_path}, ec);
        if (ec)
        {
            protect.clear();
            ec.clear();
        }
    }

    // Every complete checkpoint of THIS run: <prefix> followed by digits only.
    std::vector<std::pair<long long, fs::path>> checkpoints;
    for (const auto &entry : fs::directory_iterator{dir, ec})
    {
        if (ec)
        {
            return;
        }
        if (!entry.is_directory(ec) || ec)
        {
            ec.clear();
            continue;
        }
        const std::string name = entry.path().filename().string();
        if (name.size() <= prefix.size() ||
            name.compare(0, prefix.size(), prefix) != 0)
        {
            continue;
        }
        const std::string step = name.substr(prefix.size());
        if (step.find_first_not_of("0123456789") != std::string::npos)
        {
            continue;
        }
        checkpoints.emplace_back(std::stoll(step), entry.path());
    }

    if (static_cast<int>(checkpoints.size()) <= a_keep)
    {
        return;
    }
    std::sort(checkpoints.begin(), checkpoints.end(),
              [](const auto &a, const auto &b) { return a.first < b.first; });

    const int n_drop = static_cast<int>(checkpoints.size()) - a_keep;
    for (int i = 0; i < n_drop; ++i)
    {
        const fs::path &victim = checkpoints[i].second;

        // Still being written -> not a candidate.
        if (!fs::exists(victim / "Header", ec) || ec)
        {
            ec.clear();
            continue;
        }
        // The state this run was restarted from stays.
        if (!protect.empty() && fs::weakly_canonical(victim, ec) == protect)
        {
            ec.clear();
            continue;
        }
        ec.clear();

        fs::remove_all(victim, ec);
        if (ec)
        {
            amrex::Print() << "[checkpoint_keep] could NOT remove "
                           << victim.string() << ": " << ec.message() << '\n';
            ec.clear();
        }
        else
        {
            amrex::Print() << "[checkpoint_keep] removed " << victim.string()
                           << " (keeping newest " << a_keep << ")\n";
        }
    }
}

} // namespace CheckpointRetention

#endif /* CHECKPOINTRETENTION_HPP_ */
