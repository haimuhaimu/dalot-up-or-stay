import type { Option } from "../types/game";

type OptionsListProps = {
  options: Option[];
  onSelect: (option: Option) => void;
};

export function OptionsList({ options, onSelect }: OptionsListProps) {
  return (
    <section className="options-panel">
      {options.map((option) => (
        <button
          className="option-button"
          key={option.id}
          onClick={() => onSelect(option)}
        >
          <span>{option.label}</span>
          <small>选择</small>
        </button>
      ))}
    </section>
  );
}
