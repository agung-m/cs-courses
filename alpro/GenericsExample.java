public class GenericsExample {
    public static <T> void printArray(T[] array) {
    	for (T item: array) {
        	System.out.println(item);
        }
    }
    
    public static void main(String[] args) {
    	String[] names = {"Harry", "Potter", "Hermione"};
        Integer[] nums = {1, 3, 5, 7};
        
        printArray(names);
    
    }
	
}

