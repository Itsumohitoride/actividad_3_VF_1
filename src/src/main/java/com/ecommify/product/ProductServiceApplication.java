package com.ecommify.product;

import org.springframework.boot.SpringApplication;
import org.springframework.boot.autoconfigure.SpringBootApplication;

/**
 * Punto de entrada del microservicio de productos Ecommify.
 * <p>
 * Arranca la aplicacion Spring Boot con configuracion automatica,
 * escaneo de componentes y soporte para actuator/health.
 * </p>
 */
@SpringBootApplication
public class ProductServiceApplication {

    /**
     * Metodo principal — inicia el contexto Spring.
     *
     * @param args argumentos de linea de comandos
     */
    public static void main(String[] args) {
        SpringApplication.run(ProductServiceApplication.class, args);
    }
}
