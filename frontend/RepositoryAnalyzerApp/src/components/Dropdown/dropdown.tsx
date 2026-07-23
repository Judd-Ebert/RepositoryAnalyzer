import {useEffect, useRef, useState } from "react";


type Option = { label: string; value: string };

export type DropdownProps = {
    label: string;
    value: string;
    options: Option[];
    onChange: (value: string) => void;
    placeholder?: string;
};

export default function Dropdown({
    label,
    value,
    options,
    onChange,
    placeholder = "Select..."

}: DropdownProps) {
    const [open, setOpen] = useState(false);
    const [activeIndex, setActiveIndex] = useState(
        Math.max(0, options.findIndex(o => o.value === value)) //! What dat mean.
    );
    const rootRef = useRef<HTMLDivElement>(null);

    const selected = options.find(o => o.value === value);

    useEffect(() => {
        function onDocClick(e: MouseEvent) {
            if (!rootRef.current?.contains(e.target as Node)) setOpen(false);
        }
        document.addEventListener("mousedown", onDocClick);
        return () => document.removeEventListener("mousedown", onDocClick);
        
    }, []);

    function onKeyDown(e: React.KeyboardEvent<HTMLButtonElement>) {
        if (!open && (e.key === "ArrowDown" || e.key === "ArrowUp")) {
            setOpen(true);
            return;
        }
        if (!open) return;

        if (e.key === "ArrowDown") {
            e.preventDefault();
            setActiveIndex(i => Math.min(i + 1, options.length - 1));
        }
        if (e.key === "ArrowUp") {
            e.preventDefault();
            setActiveIndex(i => Math.max(i - 1, 0));
        }
        if (e.key === "Enter") {
            e.preventDefault();
            const next = options[activeIndex];
            if (next) {
                onChange(next.value);
                setOpen(false);
            }
        }
        if (e.key === "Escape") {
            setOpen(false);
        }
    }

    return (
        <div className="custom-dropdown" ref={rootRef}>
            <label className="selector-label">{label}</label>

            <button
            type="button"
            className="custom-dropdown-trigger"
            aria-haspopup="listbox"
            aria-expanded={open}
            onClick={() => setOpen(o => !o)}
            onKeyDown={onKeyDown}
            >
                <span>{selected?.label ?? placeholder}</span>
                <span className="custom-dropdown-arrow">{open ? "▲" : "▼"}</span>
            </button>

            {open && (

                <ul className="custom-dropdown-menu" role="listbox" aria-label={label}>
                    {options.map((opt, idx) => {
                        const isSelected = opt.value === value;
                        const isActive = idx === activeIndex;
                        return (
                            <li key={opt.value}>
                                <button
                                type="button"
                                role="option"
                                aria-selected={isSelected}
                                className={
                                    "custom-dropdown-option" +
                                    (isSelected ? " is-selected" : "") +
                                    (isActive ? " is-active" : "")
                                }
                                onMouseEnter={() => setActiveIndex(idx)}
                                onClick={() => {
                                    onChange(opt.value);
                                    setOpen(false);
                                }}
                                >
                                    {opt.label}
                                </button>
                            </li>
                        );
                    })}
                </ul>
            )}
        </div>
    );
}