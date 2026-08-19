import Sidebar from "../../components/Sidebar";
import Navbar from "../../components/Navbar";
import axios from "axios";
import React, { useState, useEffect } from "react";
import { API } from "../../utils/auth";
import { jsPDF } from "jspdf";

// ── Inline styles for teacher-unassigned warning cells ───────────────────────
const unassignedCellStyle = {
  background: "linear-gradient(135deg, #fffbeb 0%, #fef3c7 100%)",
  border: "2px solid #f59e0b",
  borderRadius: "6px",
  padding: "6px 8px",
  display: "inline-block",
  width: "100%",
  boxSizing: "border-box",
};

const unassignedBadgeStyle = {
  display: "flex",
  alignItems: "center",
  gap: "3px",
  marginTop: "3px",
  color: "#92400e",
  fontSize: "0.68rem",
  fontWeight: 600,
  lineHeight: 1.2,
};

const normalCellContentStyle = {
  display: "inline-block",
  width: "100%",
  padding: "2px 0",
};

// ── TimetableCell ────────────────────────────────────────────────────────────
// Renders a single subject cell. If teacherAssignmentStatus is "UNASSIGNED",
// renders an amber warning badge alongside the subject name so administrators
// can immediately identify slots where no teacher has been assigned.
const TimetableCell = ({ entry, subjectNameById, onHoverStart, onHoverMove, onHoverEnd }) => {
  if (!entry) {
    return <span style={{ color: "#9ca3af", fontSize: "0.75rem" }}>—</span>;
  }

  const subjectName =
    subjectNameById[entry.subjectId] ||
    entry.subjectName ||
    entry.subjectId ||
    "Unknown Subject";

  const isUnassigned =
    entry.teacherAssignmentStatus === "UNASSIGNED" ||
    (entry.teacherId === null && !entry.teacherId);

  if (isUnassigned) {
    return (
      <span
        style={unassignedCellStyle}
        title="No teacher has been assigned to this period"
        onMouseEnter={(e) => onHoverStart?.(e, entry)}
        onMouseMove={(e) => onHoverMove?.(e, entry)}
        onMouseLeave={() => onHoverEnd?.()}
      >
        <span
          style={{
            fontWeight: 600,
            fontSize: "0.82rem",
            color: "#92400e",
            display: "block",
            lineHeight: 1.3,
          }}
        >
          {subjectName}
        </span>
        <span style={unassignedBadgeStyle}>
          <span
            role="img"
            aria-label="warning"
            style={{ fontSize: "0.75rem", flexShrink: 0 }}
          >
            ⚠
          </span>
          Teacher Not Assigned
        </span>
      </span>
    );
  }

  return (
    <span
      style={normalCellContentStyle}
      onMouseEnter={(e) => onHoverStart?.(e, entry)}
      onMouseMove={(e) => onHoverMove?.(e, entry)}
      onMouseLeave={() => onHoverEnd?.()}
    >
      {subjectName}
    </span>
  );
};

// ── ViewTimetable ────────────────────────────────────────────────────────────
const ViewTimetable = () => {
  const [selectedClass, setSelectedClass] = useState("6A");
  const [selectedGrade, setSelectedGrade] = useState(6);
  const [gradeMap, setGradeMap] = useState({});
  const [currentTimetable, setCurrentTimetable] = useState(null);
  const [subjects, setSubjects] = useState([]);
  const [teachers, setTeachers] = useState([]);
  const [loading, setLoading] = useState(false);
  const [error, setError] = useState("");
  const [hasUnassigned, setHasUnassigned] = useState(false);
  const [tooltip, setTooltip] = useState({ visible: false, x: 0, y: 0, text: "" });
  const [isEditing, setIsEditing] = useState(false);
  const [isSaving, setIsSaving] = useState(false);

  const subjectNameById = subjects.reduce((lookup, subject) => {
    lookup[subject.id] = subject.subjectName;
    return lookup;
  }, {});

  const fetchSubjects = async () => {
    try {
      const response = await axios.get(`${API}/api/subjects/`);
      setSubjects(response.data || []);
    } catch (err) {
      console.log(err);
      setSubjects([]);
    }
  };

  const fetchTeachers = async () => {
    try {
      const res = await axios.get(`${API}/api/teachers/`);
      setTeachers(res.data || []);
    } catch (err) {
      console.error("Failed to fetch teachers", err);
      setTeachers([]);
    }
  };

  const fetchTimetableDoc = async () => {
    try {
      const res = await axios.get(`${API}/api/timetable/`);
      const timetableDoc = res.data?.timetable || res.data || {};

      // Build grade -> classes map from timetable keys like '6A', '7B'
      const map = {};
      Object.keys(timetableDoc).forEach((className) => {
        // extract leading digits as grade
        const match = className.match(/^(\d+)/);
        const grade = match ? Number(match[0]) : null;
        if (grade) {
          map[grade] = map[grade] || [];
          map[grade].push(className);
        }
      });

      setGradeMap(map);

      // If no selectedClass set from map, pick first available
      if (!selectedClass) {
        const firstGrade = Object.keys(map)[0];
        if (firstGrade && map[firstGrade]?.length > 0) {
          setSelectedGrade(Number(firstGrade));
          setSelectedClass(map[firstGrade][0]);
        }
      }
    } catch (err) {
      console.log(err);
    }
  };

  const fetchTimetable = async () => {
    try {
      setLoading(true);
      setError("");

      const response = await axios.get(`${API}/api/timetable/`, {
        params: {
          className: selectedClass,
        },
      });

      setCurrentTimetable(response.data);

      // Detect unassigned teacher slots.
      // When called with ?className=..., the API returns the class's day-by-day
      // object directly: { Monday: [...], Tuesday: [...], ... }
      const dayMap = response.data;
      let foundUnassigned = false;
      let missingPeriodError = "";

      const expectedDays = ["Monday", "Tuesday", "Wednesday", "Thursday", "Friday"];
      const expectedPeriods = [1, 2, 3, 4, 5, 6, 7, 8];

      if (dayMap && typeof dayMap === "object") {
        for (const day of expectedDays) {
          const dayData = dayMap[day];
          if (!dayData || !Array.isArray(dayData)) {
            missingPeriodError = `Timetable data incomplete: ${day} data is missing.`;
            break;
          }
          
          const periodsPresent = dayData.map((e) => e.period);
          for (const p of expectedPeriods) {
            if (!periodsPresent.includes(p)) {
              missingPeriodError = `Timetable data incomplete: ${day} Period ${p} is missing.`;
              break;
            }
          }
          if (missingPeriodError) break;
        }

        if (missingPeriodError) {
          throw new Error(missingPeriodError);
        }

        Object.values(dayMap).forEach((dayPeriods) => {
          if (Array.isArray(dayPeriods)) {
            dayPeriods.forEach((entry) => {
              if (
                entry?.teacherAssignmentStatus === "UNASSIGNED" ||
                (entry?.teacherId === null && entry?.subjectId)
              ) {
                foundUnassigned = true;
              }
            });
          }
        });
      }
      setHasUnassigned(foundUnassigned);
    } catch (error) {
      console.log(error);

      setError(error.message && error.message.includes("Timetable data incomplete") ? error.message : "No timetable found.");
      setCurrentTimetable(null);
      setHasUnassigned(false);
    } finally {
      setLoading(false);
    }
  };

  useEffect(() => {
    fetchSubjects();
    fetchTeachers();
    fetchTimetableDoc();

    if (selectedClass) {
      fetchTimetable();
    }
  }, [selectedClass]);

  const teacherNameById = teachers.reduce((lookup, t) => {
    if (t && t.id) lookup[t.id] = t.fullName || t.id;
    return lookup;
  }, {});

  const handleHoverStart = (e, entry) => {
    if (!entry || !entry.subjectId) return;
    const teacherId = entry.teacherId;
    if (!teacherId) return; // don't show tooltip for unassigned
    const name = teacherNameById[teacherId] || teacherId;
    setTooltip({ visible: true, x: e.clientX + 12, y: e.clientY + 12, text: name });
  };

  const handleHoverMove = (e) => {
    setTooltip((prev) => (prev.visible ? { ...prev, x: e.clientX + 12, y: e.clientY + 12 } : prev));
  };

  const handleHoverEnd = () => {
    setTooltip({ visible: false, x: 0, y: 0, text: "" });
  };

  const updateEntry = (day, period, field, value) => {
    setCurrentTimetable((previous) => {
      if (!previous) return previous;
      return {
        ...previous,
        [day]: previous[day].map((entry) =>
          entry.period === period
            ? {
                ...entry,
                [field]: value || null,
                ...(field === "teacherId"
                  ? { teacherAssignmentStatus: value ? "ASSIGNED" : "UNASSIGNED" }
                  : {}),
              }
            : entry
        ),
      };
    });
  };

  const saveTimetable = async () => {
    try {
      setIsSaving(true);
      await axios.put(`${API}/api/timetable/class/${encodeURIComponent(selectedClass)}`, {
        schedule: currentTimetable,
      });
      setIsEditing(false);
      await fetchTimetable();
      await fetchTimetableDoc();
    } catch (err) {
      setError(err.response?.data?.detail || "Failed to save timetable changes.");
    } finally {
      setIsSaving(false);
    }
  };

  const downloadPdf = () => {
    if (!currentTimetable) return;
    const pdf = new jsPDF({ orientation: "landscape", unit: "mm", format: "a4" });
    const days = ["Monday", "Tuesday", "Wednesday", "Thursday", "Friday"];
    const left = 12;
    const columnWidths = [16, 30, 44, 44, 44, 44, 44];
    let y = 16;

    pdf.setFontSize(16);
    pdf.text(`Timetable - ${selectedClass}`, left, y);
    y += 10;
    pdf.setFontSize(8);
    const headers = ["Period", "Time", ...days];
    let x = left;
    headers.forEach((header, index) => {
      pdf.setFillColor(30, 64, 175);
      pdf.setTextColor(255, 255, 255);
      pdf.rect(x, y, columnWidths[index], 8, "F");
      pdf.text(header, x + 2, y + 5);
      x += columnWidths[index];
    });
    y += 8;

    periods.forEach((period) => {
      x = left;
      const row = [
        String(period.number),
        period.time,
        ...days.map((day) => {
          const entry = getPeriodEntry(currentTimetable, day, period.number);
          const subject = subjectNameById[entry?.subjectId] || entry?.subjectId || "-";
          const teacher = teacherNameById[entry?.teacherId] || "Unassigned";
          return `${subject}\n${teacher}`;
        }),
      ];
      const rowHeight = 14;
      row.forEach((value, index) => {
        pdf.setTextColor(31, 41, 55);
        pdf.rect(x, y, columnWidths[index], rowHeight);
        pdf.text(String(value).split("\n"), x + 2, y + 5);
        x += columnWidths[index];
      });
      y += rowHeight;
    });

    pdf.save(`timetable-${selectedClass}.pdf`);
  };

  // derive available grades from gradeMap or fallback to 6-11
  const availableGrades =
    Object.keys(gradeMap).length > 0
      ? Object.keys(gradeMap).map((g) => Number(g)).sort((a, b) => a - b)
      : [6, 7, 8, 9, 10, 11];

  const periods = [
    {
      number: 1,
      time: "7:30 - 8:10",
    },
    {
      number: 2,
      time: "8:10 - 8:50",
    },
    {
      number: 3,
      time: "8:50 - 9:30",
    },
    {
      number: 4,
      time: "9:30 - 10:10",
    },
    {
      number: 5,
      time: "10:30 - 11:15",
    },
    {
      number: 6,
      time: "11:15 - 12:00",
    },
    {
      number: 7,
      time: "12:00 - 12:45",
    },
    {
      number: 8,
      time: "12:45 - 01:30",
    },
  ];

  // ── Helper: get the full period entry object for a given day+period number ──
  // When ?className=... is passed, the API returns the class day-by-day object
  // directly: { Monday: [...], Tuesday: [...], ... }
  // So currentTimetable IS the class schedule — no extra unwrapping needed.
  const getPeriodEntry = (timetable, day, periodNumber) => {
    if (!timetable || typeof timetable !== "object") return null;
    const dayData = timetable[day];
    if (!Array.isArray(dayData)) return null;
    return dayData.find((item) => item.period === periodNumber) || null;
  };

  return (
    <div className="flex">
      <Sidebar />
      <div className="flex-1">
        <Navbar />
        <div className="p-8 bg-gray-100 min-h-screen">
          <h3 className="text-2xl font-semibold mb-6 text-gray-800">
            View Timetable
          </h3>

          <div className="bg-white rounded-xl shadow-md p-6 mb-6">
            <div className="flex items-center gap-4">
              <label className="font-semibold">Grade</label>

              <select
                value={selectedGrade}
                onChange={(e) => {
                  const g = Number(e.target.value);
                  setSelectedGrade(g);
                  // pick first class in this grade if available
                  const classes = gradeMap[g] || [];
                  if (classes.length > 0) setSelectedClass(classes[0]);
                }}
                className="border px-4 py-2 rounded"
              >
                {availableGrades.map((grade) => (
                  <option key={grade} value={grade}>
                    {grade}
                  </option>
                ))}
              </select>

              {/* class selector if multiple classes per grade */}
              {gradeMap[selectedGrade] && (
                <select
                  value={selectedClass}
                  onChange={(e) => setSelectedClass(e.target.value)}
                  className="border px-4 py-2 rounded"
                >
                  {gradeMap[selectedGrade].map((cls) => (
                    <option key={cls} value={cls}>
                      {cls}
                    </option>
                  ))}
                </select>
              )}
            </div>
          </div>

          {loading && <p>Loading timetable...</p>}

          {error && <p className="text-red-500">{error}</p>}

          {/* ── Unassigned teacher warning banner ───────────────────────────── */}
          {currentTimetable && hasUnassigned && (
            <div
              style={{
                background: "#fffbeb",
                border: "1.5px solid #f59e0b",
                borderRadius: "8px",
                padding: "12px 16px",
                marginBottom: "16px",
                display: "flex",
                alignItems: "flex-start",
                gap: "10px",
              }}
            >
              <span style={{ fontSize: "1.1rem", marginTop: "1px" }}>⚠️</span>
              <div>
                <span
                  style={{
                    fontWeight: 700,
                    color: "#92400e",
                    fontSize: "0.9rem",
                  }}
                >
                  Some periods have no teacher assigned.
                </span>
                <span
                  style={{
                    color: "#78350f",
                    fontSize: "0.85rem",
                    marginLeft: "6px",
                  }}
                >
                  These slots are highlighted in amber below. Subjects are
                  scheduled but require a teacher to be assigned manually.
                </span>
              </div>
            </div>
          )}

          {currentTimetable && (
            <div className="bg-white rounded-xl shadow-md p-6">
              <div className="flex flex-wrap items-center justify-between gap-3 mb-5">
                <h4 className="text-lg font-semibold">Timetable - {selectedClass}</h4>
                <div className="flex flex-wrap gap-2">
                  {!isEditing ? (
                    <button type="button" onClick={() => setIsEditing(true)} className="px-4 py-2 rounded bg-blue-700 text-white hover:bg-blue-800">
                      Edit Timetable
                    </button>
                  ) : (
                    <>
                      <button type="button" onClick={() => { setIsEditing(false); fetchTimetable(); }} className="px-4 py-2 rounded border border-gray-300">
                        Cancel
                      </button>
                      <button type="button" onClick={saveTimetable} disabled={isSaving} className="px-4 py-2 rounded bg-green-700 text-white disabled:opacity-60">
                        {isSaving ? "Saving..." : "Save Changes"}
                      </button>
                    </>
                  )}
                  <button type="button" onClick={downloadPdf} className="px-4 py-2 rounded bg-gray-800 text-white hover:bg-gray-900">
                    Download PDF
                  </button>
                </div>
              </div>

              <div className="overflow-x-auto">
                <table className="min-w-full border border-gray-400">
                  <thead>
                    <tr>
                      <th className="border px-4 py-3">Period</th>

                      <th className="border px-4 py-3">Time</th>

                      <th className="border px-4 py-3">Monday</th>

                      <th className="border px-4 py-3">Tuesday</th>

                      <th className="border px-4 py-3">Wednesday</th>

                      <th className="border px-4 py-3">Thursday</th>

                      <th className="border px-4 py-3">Friday</th>
                    </tr>
                  </thead>

                  <tbody>
                    {periods.map((p) => {
                      return (
                        <React.Fragment key={p.number}>
                          <tr>
                            <td className="border px-4 py-3 text-center">
                              {p.number}
                            </td>
                            <td className="border px-4 py-3 text-center">
                              {p.time}
                            </td>
                            {["Monday", "Tuesday", "Wednesday", "Thursday", "Friday"].map(
                              (day) => {
                                const entry = getPeriodEntry(
                                  currentTimetable,
                                  day,
                                  p.number
                                );
                                return (
                                  <td
                                    key={day}
                                    className="border px-3 py-2 text-center"
                                    style={
                                      entry?.teacherAssignmentStatus ===
                                        "UNASSIGNED" ||
                                      (entry?.teacherId === null &&
                                        entry?.subjectId)
                                        ? {
                                            background:
                                              "linear-gradient(135deg, #fffbeb 0%, #fef3c7 100%)",
                                          }
                                        : {}
                                    }
                                  >
                                    {isEditing ? (
                                      <div className="space-y-1">
                                        <select
                                          value={entry?.subjectId || ""}
                                          onChange={(e) => updateEntry(day, p.number, "subjectId", e.target.value)}
                                          className="w-full border rounded px-1 py-1 text-xs"
                                        >
                                          <option value="">No subject</option>
                                          {subjects.map((subject) => (
                                            <option key={subject.id} value={subject.id}>{subject.subjectName}</option>
                                          ))}
                                        </select>
                                        <select
                                          value={entry?.teacherId || ""}
                                          onChange={(e) => updateEntry(day, p.number, "teacherId", e.target.value)}
                                          className="w-full border rounded px-1 py-1 text-xs"
                                        >
                                          <option value="">Unassigned</option>
                                          {teachers.map((teacher) => (
                                            <option key={teacher.id} value={teacher.id}>{teacher.fullName}</option>
                                          ))}
                                        </select>
                                      </div>
                                    ) : (
                                      <TimetableCell
                                        entry={entry}
                                        subjectNameById={subjectNameById}
                                        onHoverStart={handleHoverStart}
                                        onHoverMove={handleHoverMove}
                                        onHoverEnd={handleHoverEnd}
                                      />
                                    )}
                                  </td>
                                );
                              }
                            )}
                          </tr>

                          {/* Insert interval row visually after period 4 */}
                          {p.number === 4 && (
                            <tr style={{ background: "#f0fdf4" }}>
                              <td className="border px-4 py-3 text-center">
                                —
                              </td>
                              <td className="border px-4 py-3 text-center font-semibold">
                                10:10 - 10:30
                              </td>
                              {["Monday", "Tuesday", "Wednesday", "Thursday", "Friday"].map(
                                (day) => (
                                  <td
                                    key={day}
                                    className="border px-4 py-3 text-center font-semibold text-green-700"
                                  >
                                    Interval
                                  </td>
                                )
                              )}
                            </tr>
                          )}
                        </React.Fragment>
                      );
                    })}
                  </tbody>
                </table>
              </div>

              {/* ── Legend ──────────────────────────────────────────────────── */}
              <div
                style={{
                  marginTop: "16px",
                  display: "flex",
                  alignItems: "center",
                  gap: "24px",
                  flexWrap: "wrap",
                }}
              >
                <div
                  style={{
                    display: "flex",
                    alignItems: "center",
                    gap: "8px",
                    fontSize: "0.8rem",
                    color: "#374151",
                  }}
                >
                  <span
                    style={{
                      width: "16px",
                      height: "16px",
                      background: "white",
                      border: "1px solid #d1d5db",
                      borderRadius: "3px",
                      flexShrink: 0,
                    }}
                  />
                  Normal period
                </div>
                <div
                  style={{
                    display: "flex",
                    alignItems: "center",
                    gap: "8px",
                    fontSize: "0.8rem",
                    color: "#92400e",
                  }}
                >
                  <span
                    style={{
                      width: "16px",
                      height: "16px",
                      background:
                        "linear-gradient(135deg, #fffbeb 0%, #fef3c7 100%)",
                      border: "2px solid #f59e0b",
                      borderRadius: "3px",
                      flexShrink: 0,
                    }}
                  />
                  ⚠ Teacher Not Assigned — subject is scheduled, teacher must
                  be assigned manually
                </div>
                <div
                  style={{
                    display: "flex",
                    alignItems: "center",
                    gap: "8px",
                    fontSize: "0.8rem",
                    color: "#065f46",
                  }}
                >
                  <span
                    style={{
                      width: "16px",
                      height: "16px",
                      background: "#f0fdf4",
                      border: "1px solid #6ee7b7",
                      borderRadius: "3px",
                      flexShrink: 0,
                    }}
                  />
                  Interval break
                </div>
              </div>
            </div>
          )}
        </div>
      </div>
      {/* Tooltip popup (follows cursor) */}
      {tooltip.visible && (
        <div
          role="tooltip"
          aria-hidden={!tooltip.visible}
          style={{
            position: "fixed",
            left: tooltip.x,
            top: tooltip.y,
            zIndex: 2000,
            background: "rgba(0,0,0,0.85)",
            color: "white",
            padding: "6px 8px",
            borderRadius: 6,
            fontSize: "0.85rem",
            pointerEvents: "none",
            boxShadow: "0 4px 12px rgba(0,0,0,0.15)",
            whiteSpace: "nowrap",
          }}
        >
          {tooltip.text}
        </div>
      )}
    </div>
  );
};

export default ViewTimetable;
