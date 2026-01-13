import React, { useState, useEffect } from 'react';
import JournalList from '../components/journal/JournalList';
import JournalEntryForm from '../components/journal/JournalEntryForm';
import { getJournalEntries, createJournalEntry, updateJournalEntry, analyzeJournalEntry } from '../services/api';

const Journal = () => {
    const [entries, setEntries] = useState([]);
    const [selectedEntry, setSelectedEntry] = useState(null);
    const [isLoading, setIsLoading] = useState(true);

    useEffect(() => {
        loadEntries();
    }, []);

    const loadEntries = async () => {
        setIsLoading(true);
        try {
            const data = await getJournalEntries();
            setEntries(data);
        } catch (error) {
            console.error("Failed to load journal entries:", error);
        } finally {
            setIsLoading(false);
        }
    };

    const handleSelectEntry = (entry) => {
        setSelectedEntry(entry);
    };

    const handleNewEntry = () => {
        setSelectedEntry(null);
    };

    const handleSaveEntry = async (entryData) => {
        try {
            if (selectedEntry) {
                // Update
                const updated = await updateJournalEntry(selectedEntry.id, entryData);
                setEntries(entries.map(e => e.id === updated.id ? updated : e));
                setSelectedEntry(updated);
            } else {
                // Create
                const created = await createJournalEntry(entryData);
                setEntries([created, ...entries]);
                setSelectedEntry(created);
            }
        } catch (error) {
            console.error("Failed to save entry:", error);
        }
    };

    const handleAnalyzeEntry = async (entryId) => {
        try {
            const analyzed = await analyzeJournalEntry(entryId);
            setEntries(entries.map(e => e.id === analyzed.id ? analyzed : e));
            setSelectedEntry(analyzed);
        } catch (error) {
            console.error("Failed to analyze entry:", error);
        }
    };

    return (
        <div className="flex h-screen bg-gray-950 text-white overflow-hidden">
            <JournalList
                entries={entries}
                onSelectEntry={handleSelectEntry}
                onNewEntry={handleNewEntry}
            />

            <JournalEntryForm
                entry={selectedEntry}
                onSave={handleSaveEntry}
                onAnalyze={handleAnalyzeEntry}
            />
        </div>
    );
};

export default Journal;
