"use client";

import { Check } from "lucide-react";

import type { WorkflowStep } from "@/types/dashboard";

export function WorkflowStepper({
  steps,
  activeStep = 1,
}: {
  steps: WorkflowStep[];
  activeStep?: number;
}) {
  // Progress line width percentage based on activeStep (1 to steps.length)
  const progressPercent =
    steps.length > 1 ? Math.min(100, Math.max(0, ((activeStep - 1) / (steps.length - 1)) * 100)) : 0;

  return (
    <section className="rounded-2xl border border-slate-200 bg-white p-4 shadow-sm sm:p-6">
      <div className="relative">
        {/* Background Connecting Line (centered for 3 columns) */}
        <div className="absolute left-[16.66%] right-[16.66%] top-4 hidden h-0.5 bg-slate-200 sm:block" />

        {/* Active Progress Connecting Line */}
        <div
          className="absolute left-[16.66%] top-4 hidden h-0.5 bg-blue-600 transition-all duration-500 ease-in-out sm:block"
          style={{ width: `calc(${progressPercent}% * 0.6666)` }}
        />

        {/* Steps Grid (3 Columns) */}
        <div className="relative grid gap-4 sm:grid-cols-3 sm:gap-0">
          {steps.map((step, index) => {
            const stepNum = index + 1;
            const isCompleted = stepNum < activeStep || (activeStep >= 3 && stepNum <= 3);
            const isActive = stepNum === activeStep && !isCompleted;
            const isPending = !isCompleted && !isActive;

            return (
              <div
                className={`relative flex items-center gap-3 rounded-xl p-2 transition-all sm:flex-col sm:p-0 sm:text-center ${
                  isPending ? "opacity-50" : "opacity-100"
                }`}
                key={step.title}
              >
                {/* Step Circle Badge */}
                <span
                  className={`grid size-8 shrink-0 place-items-center rounded-full text-xs font-bold transition-all duration-300 ${
                    isCompleted
                      ? "bg-emerald-600 text-white shadow-md shadow-emerald-600/25 ring-4 ring-emerald-50"
                      : isActive
                      ? "bg-blue-600 text-white shadow-md shadow-blue-600/30 ring-4 ring-blue-100 animate-pulse"
                      : "bg-slate-100 text-slate-500 border border-slate-200"
                  }`}
                >
                  {isCompleted ? <Check size={16} strokeWidth={3} /> : stepNum}
                </span>

                {/* Step Content */}
                <div>
                  <p
                    className={`text-sm font-semibold ${
                      isCompleted
                        ? "text-emerald-700 font-bold"
                        : isActive
                        ? "text-blue-700 font-bold"
                        : "text-slate-700"
                    }`}
                  >
                    {step.title}
                  </p>
                  <p className="mt-0.5 text-xs leading-5 text-slate-500">{step.description}</p>
                </div>
              </div>
            );
          })}
        </div>
      </div>
    </section>
  );
}
