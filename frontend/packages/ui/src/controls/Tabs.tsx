import * as RadixTabs from "@radix-ui/react-tabs";
import type { ReactNode } from "react";
import { useState } from "react";

export interface TabItem {
  value: string;
  label: string;
  content: ReactNode;
}

export interface TabsProps {
  tabs: TabItem[];
  defaultValue: string;
  onValueChange?: (value: string) => void;
}

export function Tabs({ tabs, defaultValue, onValueChange }: TabsProps) {
  const [value, setValue] = useState(defaultValue);
  const change = (next: string) => {
    setValue(next);
    onValueChange?.(next);
  };
  return (
    <RadixTabs.Root value={value} onValueChange={change}>
      <RadixTabs.List className="tabs">
        {tabs.map((tab) => (
          <RadixTabs.Trigger key={tab.value} value={tab.value} className={tab.value === value ? "tab active" : "tab"}>
            {tab.label}
          </RadixTabs.Trigger>
        ))}
      </RadixTabs.List>
      {tabs.map((tab) => (
        <RadixTabs.Content key={tab.value} value={tab.value}>
          {tab.content}
        </RadixTabs.Content>
      ))}
    </RadixTabs.Root>
  );
}
