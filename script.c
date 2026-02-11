#include "nauty.h"
#include "nausparse.h"
#include <stdio.h>
#include <stdlib.h>
#include <string.h>

/* -------------------------------------------------- */
/* Lecture graphe + couleurs                          */
/* -------------------------------------------------- */

void read_graph_and_colors(const char *filename,
                           sparsegraph *g,
                           int **colors_out)
{
    FILE *f = fopen(filename, "r");
    if (!f)
    {
        perror(filename);
        exit(1);
    }

    int n;
    if (fscanf(f, "%d\n", &n) != 1)
    {
        printf("Erreur lecture n dans %s\n", filename);
        exit(1);
    }

    SG_INIT(*g);
    g->nv = n;

    /* stockage temporaire des arêtes */
    int capacity = n * n;
    int *edges = malloc(capacity * sizeof(int));
    int edge_count = 0;

    char line[1024];

    /* Lecture listes d'adjacence */
    for (int v = 0; v < n; v++)
    {
        if (!fgets(line, sizeof(line), f))
        {
            printf("Erreur ligne sommet %d\n", v);
            exit(1);
        }

        char *ptr = line;
        int w;

        while (sscanf(ptr, "%d", &w) == 1)
        {
            edges[edge_count++] = w;

            while (*ptr && *ptr != ' ') ptr++;
            while (*ptr == ' ') ptr++;
        }
    }

    /* Allocation sparsegraph */
    SG_ALLOC(*g, n, edge_count, "malloc");
    g->nde = edge_count;

    int pos = 0;
    int eindex = 0;

    for (int v = 0; v < n; v++)
    {
        g->v[v] = pos;
        g->d[v] = 0;

        while (eindex < edge_count)
        {
            g->e[pos++] = edges[eindex++];
            g->d[v]++;
            if (pos >= edge_count) break;
            if (g->d[v] >= n) break; /* sécurité */
        }
    }

    free(edges);

    /* Lecture couleurs */
    int *colors = malloc(n * sizeof(int));

    char word[100];
    int found = 0;

    while (fscanf(f, "%s", word) == 1)
    {
        if (strcmp(word, "colors") == 0)
        {
            for (int i = 0; i < n; i++)
                fscanf(f, "%d", &colors[i]);
            found = 1;
            break;
        }
    }

    if (!found)
    {
        printf("Pas de section colors dans %s\n", filename);
        exit(1);
    }

    fclose(f);
    *colors_out = colors;
}

/* -------------------------------------------------- */
/* Construction partition à partir des couleurs       */
/* -------------------------------------------------- */

void build_partition(int *colors, int n, int *lab, int *ptn)
{
    int pos = 0;
    int maxc = 0;

    for (int i = 0; i < n; i++)
        if (colors[i] > maxc) maxc = colors[i];

    for (int c = 0; c <= maxc; c++)
    {
        int start = pos;

        for (int v = 0; v < n; v++)
            if (colors[v] == c)
                lab[pos++] = v;

        for (int i = start; i < pos; i++)
            ptn[i] = 1;

        if (pos > start)
            ptn[pos - 1] = 0;
    }
}

/* -------------------------------------------------- */
/* Main                                               */
/* -------------------------------------------------- */

int main(int argc, char *argv[])
{
    if (argc != 3)
    {
        printf("Usage: %s g1.txt g2.txt\n", argv[0]);
        return 1;
    }

    sparsegraph g1, g2, cg1, cg2;
    SG_INIT(g1);
    SG_INIT(g2);
    SG_INIT(cg1);
    SG_INIT(cg2);

    int *colors1, *colors2;

    read_graph_and_colors(argv[1], &g1, &colors1);
    read_graph_and_colors(argv[2], &g2, &colors2);

    if (g1.nv != g2.nv)
    {
        printf("Non isomorphes (nv différent)\n");
        return 0;
    }

    int n = g1.nv;

    int *lab1 = malloc(n * sizeof(int));
    int *ptn1 = malloc(n * sizeof(int));
    int *lab2 = malloc(n * sizeof(int));
    int *ptn2 = malloc(n * sizeof(int));
    int *orbits = malloc(n * sizeof(int));

    build_partition(colors1, n, lab1, ptn1);
    build_partition(colors2, n, lab2, ptn2);

    static DEFAULTOPTIONS_SPARSEGRAPH(options);
    statsblk stats;
    options.getcanon = TRUE;

    sparsenauty(&g1, lab1, ptn1, orbits, &options, &stats, &cg1);
    sparsenauty(&g2, lab2, ptn2, orbits, &options, &stats, &cg2);

    if (aresame_sg(&cg1, &cg2))
        printf("Isomorphes\n");
    else
        printf("Non isomorphes\n");

    /* nettoyage */
    SG_FREE(g1);
    SG_FREE(g2);
    SG_FREE(cg1);
    SG_FREE(cg2);

    free(colors1);
    free(colors2);
    free(lab1);
    free(ptn1);
    free(lab2);
    free(ptn2);
    free(orbits);

    return 0;
}
