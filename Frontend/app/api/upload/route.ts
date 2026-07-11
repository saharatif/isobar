import { NextResponse } from "next/server";

export async function POST() {
  return NextResponse.json(
    {
      error: "Upload backend is not connected yet",
      requiredEnv: "NEXT_PUBLIC_API_BASE_URL"
    },
    { status: 501 }
  );
}
