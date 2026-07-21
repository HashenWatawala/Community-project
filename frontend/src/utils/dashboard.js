import { API } from "./auth";

export const fetchTeachersCount = async () => {
    try {
        const resp = await fetch(`${API}/api/teachers/`, {
            method: "GET",
            headers: { "Content-Type": "application/json" },
        });
        if (!resp.ok) {
            throw new Error("Failed to fetch teachers");
        }
        const data = await resp.json();
        return data.length;
    } catch (error) {
        console.error("Error fetching teachers count:", error);
        return 0;
    }
};

export const fetchClassesCount = async () => {
    try {
        const resp = await fetch(`${API}/api/subjects/`, {
            method: "GET",
            headers: { "Content-Type": "application/json" },
        });
        if (!resp.ok) {
            throw new Error("Failed to fetch subjects");
        }
        const data = await resp.json();
        // Count unique grades from subjects
        const uniqueGrades = new Set(data.map((subject) => subject.grade));
        return uniqueGrades.size;
    } catch (error) {
        console.error("Error fetching classes count:", error);
        return 0;
    }
};
