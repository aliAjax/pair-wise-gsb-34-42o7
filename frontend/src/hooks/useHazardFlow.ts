import { useCallback } from "react";
import { useHazardTicketStore } from "../stores/HazardTicketStore";
import { useFireDeviceStore } from "../stores/FireDeviceStore";
import { OPEN_RECTIFY_STATUSES } from "../constants/RectifyStatus";
import type { HazardTicket } from "../types/HazardTicket";

export function useHazardFlow() {
  const hazards = useHazardTicketStore();
  const devices = useFireDeviceStore();
  const close = useCallback(async (ticketId: number, rectifyNote: string) => {
    await hazards.close(ticketId, rectifyNote);
    // 关单后设备台账状态重算，台账同步刷新
    await devices.load();
  }, [hazards, devices]);
  const isOpen = (row: HazardTicket) => OPEN_RECTIFY_STATUSES.includes(row.rectify_status as never);
  return { hazards, devices, close, isOpen };
}
