import prompts from '../../config/prompts';

export default function handler(req, res) {
  if (req.method === 'POST') {
    const { message, context } = req.body;
    const prompt = prompts[context] || prompts['family'];
    const response = `Refined message: ${message} (using ${context} context with ${prompt})`; // Placeholder; replace with AI call
    res.status(200).json({ refined: response });
  } else {
    res.status(405).json({ error: 'Method not allowed' });
  }
}
