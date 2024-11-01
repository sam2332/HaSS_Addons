function extractMoods(text) {
    // Define regex patterns to capture a single word after mood-indicating phrases
    const patterns = [
        /\bIt makes me feel so (\w+)\b/gi,
        /\bI feel so (\w+)\b/gi,
        /\bMakes me feel (\w+)\b/gi,
        /\bI'm feeling so (\w+)\b/gi,
        /\bI am feeling so (\w+)\b/gi,
        /\bIt makes me feel (\w+)\b/gi,
        /\bI'm feeling (\w+)\b/gi,
        /\bI feel (\w+)\b/gi,
        /\bIt makes me (\w+)\b/gi,
        /\bI've been feeling (\w+)\b/gi,
        /\bI am (\w+)\b/gi,
        /\bI'm (\w+)\b/gi,
        /\bFeeling (\w+)\b/gi,
        /\bThis leaves me (\w+)\b/gi,
        /\bLeft me feeling (\w+)\b/gi,
        /\bI am left feeling (\w+)\b/gi,
        /\bMy mood is (\w+)\b/gi,
        /\bThis makes me (\w+)\b/gi,
        /\bI can't help but feel (\w+)\b/gi,
        /\bI was feeling (\w+)\b/gi
    ];

    // Array to collect all matched moods
    let moods = [];

    // Iterate over each pattern
    for (const pattern of patterns) {
        let match;
        // Use the pattern to capture single-word moods
        while ((match = pattern.exec(text)) !== null) {
            // Add each found mood
            moods.push(match[1]);
        }
    }

    // Handle cases where multiple moods are found
    if (moods.length > 1) {
        // Find the most common mood or return the first one
        if (moods.length > 2) {
            const moodCounts = {};
            moods.forEach(function(m) {
                moodCounts[m] = (moodCounts[m] || 0) + 1;
            });
            moods = Object.keys(moodCounts).reduce((a, b) => (moodCounts[a] > moodCounts[b] ? a : b));
        } else {
            moods = moods[0];
        }
    } else {
        // If only one mood, return it directly
        moods = moods.length ? moods[0] : null;
    }

    return moods;
}
