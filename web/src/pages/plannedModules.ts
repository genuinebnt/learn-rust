import { useState } from "react";
import type { CourseOverview } from "../api";
import { getPref, setPref } from "../prefs";

/** Whether the course tree also lists the modules that are still planned (being rewritten). Off by default, remembered in this browser. */
export function useShowPlanned(): [boolean, (on: boolean) => void] {
    const [on, setOn] = useState<boolean>(() => getPref("course.showPlanned", false));
    return [
        on,
        (v) => {
            setOn(v);
            setPref("course.showPlanned", v);
        },
    ];
}

export function plannedCount(c: CourseOverview | undefined): number {
    return c?.projects.flatMap((p) => p.modules).filter((m) => m.planned).length ?? 0;
}

/** The course without its planned modules (and without projects that have none left), its totals recounted; unchanged when `show` is on. */
export function withoutPlanned(c: CourseOverview | undefined, show: boolean): CourseOverview | undefined {
    if (!c || show) return c;
    const projects = c.projects.map((p) => ({ ...p, modules: p.modules.filter((m) => !m.planned) })).filter((p) => p.modules.length > 0 || !p.planned);
    const stages = projects.flatMap((p) => p.modules).flatMap((m) => m.stages);
    return { ...c, projects: projects.filter((p) => p.modules.length > 0), total: stages.length, done: stages.filter((s) => s.state !== "todo").length };
}
