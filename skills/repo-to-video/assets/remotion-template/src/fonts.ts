import {loadFont as loadInter} from '@remotion/google-fonts/Inter';
import {loadFont as loadJetBrainsMono} from '@remotion/google-fonts/JetBrainsMono';

// Register the fonts used by the template so rendering is deterministic and
// never silently falls back to whatever is installed on the render machine.
loadInter('normal', {weights: ['400', '500', '700', '800'], subsets: ['latin']});
loadJetBrainsMono('normal', {weights: ['400'], subsets: ['latin']});
