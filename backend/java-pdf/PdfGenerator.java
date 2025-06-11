import org.xhtmlrenderer.pdf.ITextRenderer;
import java.io.*;
import java.nio.file.Files;
import java.nio.file.Paths;

public class PdfGenerator {
    public static void main(String[] args) {
        if (args.length != 2) {
            System.err.println("Usage: java PdfGenerator <html-file> <output-pdf>");
            System.exit(1);
        }
        
        String htmlFile = args[0];
        String outputPdf = args[1];
        
        try {
            // Read HTML content
            String htmlContent = new String(Files.readAllBytes(Paths.get(htmlFile)));
            
            // Generate PDF using Flying Saucer
            ITextRenderer renderer = new ITextRenderer();
            renderer.setDocumentFromString(htmlContent);
            renderer.layout();
            
            // Write PDF to output stream
            FileOutputStream os = new FileOutputStream(outputPdf);
            renderer.createPDF(os);
            os.close();
            
            System.out.println("SUCCESS: PDF generated at " + outputPdf);
            
        } catch (Exception e) {
            System.err.println("ERROR: " + e.getMessage());
            e.printStackTrace();
            System.exit(1);
        }
    }
}