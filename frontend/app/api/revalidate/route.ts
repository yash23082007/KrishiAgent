import { NextRequest, NextResponse } from "next/server";
import { revalidatePath } from "next/cache";

export async function GET(request: NextRequest) {
  const secret = request.nextUrl.searchParams.get("secret");
  const path = request.nextUrl.searchParams.get("path") || "/";

  // Quick verify checks (standard for next.js revalidate routes)
  if (secret !== process.env.REVALIDATION_TOKEN && process.env.NODE_ENV === "production") {
    return NextResponse.json({ message: "Invalid verification token" }, { status: 401 });
  }

  try {
    revalidatePath(path);
    return NextResponse.json({ revalidated: true, path, now: Date.now() });
  } catch (err: any) {
    return NextResponse.json({ message: err.message }, { status: 500 });
  }
}
