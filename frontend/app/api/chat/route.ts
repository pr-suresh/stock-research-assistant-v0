const BACKEND_URL = process.env.NEXT_PUBLIC_BACKEND_URL || 'http://localhost:8000';

export async function POST(req: Request) {
  try {
    const { messages } = await req.json();

    // Get the last user message
    const lastMessage = messages[messages.length - 1];

    // Call backend agent API
    const response = await fetch(`${BACKEND_URL}/agent/query`, {
      method: 'POST',
      headers: {
        'Content-Type': 'application/json',
      },
      body: JSON.stringify({
        question: lastMessage.content,
        max_iterations: 5,
      }),
    });

    if (!response.ok) {
      const error = await response.text();
      return new Response(
        JSON.stringify({ error: `Backend error: ${error}` }),
        { status: response.status, headers: { 'Content-Type': 'application/json' } }
      );
    }

    const data = await response.json();

    // Format the response as a message
    const formattedMessage = {
      id: Date.now().toString(),
      role: 'assistant',
      content: data.answer,
      toolCalls: data.tool_calls,
      metadata: data.metadata,
    };

    // Return as JSON for now (we can add streaming later)
    return new Response(
      JSON.stringify(formattedMessage),
      { headers: { 'Content-Type': 'application/json' } }
    );
  } catch (error: any) {
    console.error('Chat API error:', error);
    return new Response(
      JSON.stringify({ error: error.message || 'Internal server error' }),
      { status: 500, headers: { 'Content-Type': 'application/json' } }
    );
  }
}
