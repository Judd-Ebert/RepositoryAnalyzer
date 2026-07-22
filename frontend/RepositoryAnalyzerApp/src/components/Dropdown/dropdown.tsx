import {useEffect, useRef, useState } from "react";


type Option = { label: string; value: string };

type DropdownProps = {
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
        Math.max(0, options.findIndex(o => o.value === value))
    );
}