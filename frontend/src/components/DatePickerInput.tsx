import { forwardRef } from "react";
import DatePicker from "react-datepicker";
import "react-datepicker/dist/react-datepicker.css";

type DatePickerInputProps = {
  value: Date | null;
  onChange: (date: Date | null) => void;
  placeholder?: string;
  className?: string;
  minDate?: Date;
  maxDate?: Date;
};

const DatePickerInput = forwardRef<InstanceType<typeof DatePicker>, DatePickerInputProps>(
  ({ value, onChange, placeholder, className = "", minDate, maxDate }, ref) => {
    return (
      <DatePicker
        selected={value}
        onChange={onChange}
        dateFormat="dd. MMM yyyy"
        placeholderText={placeholder}
        className={`w-full cursor-pointer rounded-2xl border border-slate-200 px-4 py-3 text-base shadow-inner focus:border-indigo-400 focus:outline-none ${className}`}
        calendarClassName="tg-datepicker"
        popperClassName="tg-datepicker-popper"
        wrapperClassName="w-full"
        minDate={minDate}
        maxDate={maxDate}
        ref={ref}
        showPopperArrow={false}
        formatWeekDay={(nameOfDay) => nameOfDay.slice(0, 2)}
        isClearable
        clearButtonTitle="Clear date"
        todayButton="Today"
      />
    );
  }
);

DatePickerInput.displayName = "DatePickerInput";

export default DatePickerInput;
